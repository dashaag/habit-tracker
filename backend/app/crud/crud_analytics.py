from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func, case, and_, Date, cast, select
from datetime import datetime, timedelta, date as DDate # Alias to avoid confusion
from typing import List, Dict, Any, Optional
import calendar

from app.models.habit import Habit, HabitTrackingLog, HabitCategory # Corrected import for HabitCategory
from app.schemas.analytics import SummaryStats, HabitProgressData, CategoryDistributionData, HabitPerformanceItem, ChartDataset, PieChartDataset

# Helper function to determine date range based on time_period string
def get_date_range(time_period: str, current_date: Optional[datetime] = None) -> tuple[datetime, datetime]:
    if current_date is None:
        current_date = datetime.utcnow()
    
    end_date = current_date

    if time_period.lower() == "month":
        start_date = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # To get the actual end of the month, not just 30 days back for current month view
        # end_date = (start_date + timedelta(days=calendar.monthrange(start_date.year, start_date.month)[1])) - timedelta(microseconds=1)
    elif time_period.lower() == "week":
        start_date = (current_date - timedelta(days=current_date.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_period.lower() == "day":
        start_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_period.lower() == "year":
        start_date = current_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else: # Default to current month
        start_date = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    return start_date, end_date

async def get_summary_stats(db: AsyncSession, user_id: int, time_period: str, habit_id_filter: Optional[int] = None) -> SummaryStats:
    start_date, end_date = get_date_range(time_period)

    # Base query for logs
    log_stmt = select(func.count(HabitTrackingLog.id)).filter(
        HabitTrackingLog.user_id == user_id,
        HabitTrackingLog.logged_datetime >= start_date,
        HabitTrackingLog.logged_datetime <= end_date
    )

    # Base query for habits
    habit_stmt = select(func.count(Habit.id)).filter(Habit.user_id == user_id)

    if habit_id_filter is not None:
        log_stmt = log_stmt.filter(HabitTrackingLog.habit_id == habit_id_filter)
        habit_stmt = habit_stmt.filter(Habit.id == habit_id_filter)

    total_completions_result = await db.execute(log_stmt)
    total_completions = total_completions_result.scalar_one() or 0

    active_habits_result = await db.execute(habit_stmt)
    active_habits = active_habits_result.scalar_one() or 0
    
    avg_per_habit = (total_completions / active_habits) if active_habits > 0 else 0

    # Day streak is complex and needs dedicated logic, placeholder for now
    # It would involve checking consecutive days with completed logs for specific habits or overall.
    day_streak = 0 

    return SummaryStats(
        total_completions=total_completions,
        day_streak=day_streak, 
        avg_per_habit=round(avg_per_habit, 2),
        active_habits=active_habits
    )

async def get_habit_progress_data(db: AsyncSession, user_id: int, time_period: str, habit_id_filter: Optional[int] = None) -> HabitProgressData:
    start_date, end_date = get_date_range(time_period)

    # Determine labels based on time_period
    labels: List[str] = []
    date_format_str = "%b %d" # Default for month/week
    if time_period.lower() == "day":
        labels = [(start_date + timedelta(hours=i)).strftime("%H:00") for i in range(24)]
        date_group_func = func.strftime('%Y-%m-%d %H:00:00', HabitTrackingLog.logged_datetime)
    elif time_period.lower() == "year":
        labels = [DDate(start_date.year, i, 1).strftime("%b") for i in range(1, 13)]
        date_group_func = func.strftime('%Y-%m', HabitTrackingLog.logged_datetime) # Group by month for year view
    else: # Default to month view if time_period is unrecognized
        days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
        labels = [(start_date + timedelta(days=i)).strftime(date_format_str) for i in range(days_in_month)]
        date_group_func = cast(HabitTrackingLog.logged_datetime, Date)

    # Base query for logs, grouped by the determined date_group_func
    stmt_select = select(
        date_group_func.label("date_group"),
        HabitTrackingLog.habit_id.label("habit_id"),
        func.count(HabitTrackingLog.id).label("completions"),
    ).filter(
        HabitTrackingLog.user_id == user_id,
        HabitTrackingLog.logged_datetime >= start_date,
        HabitTrackingLog.logged_datetime <= end_date,
    ).group_by("date_group", "habit_id")

    # Fetch active habits for the user to iterate over for datasets
    user_habits_stmt = select(Habit).filter(Habit.user_id == user_id)

    if habit_id_filter is not None: # habit_id_filter is Optional[int]
        stmt_select = stmt_select.filter(HabitTrackingLog.habit_id == habit_id_filter)
        user_habits_stmt = user_habits_stmt.filter(Habit.id == habit_id_filter)

    log_results_exec = await db.execute(stmt_select)
    log_results = log_results_exec.all() # list of Row objects with date_group, habit_id, completions

    user_habits_exec = await db.execute(user_habits_stmt)
    user_habits = user_habits_exec.scalars().all() # list of Habit objects

    datasets: List[ChartDataset] = []

    # Prepare a map of completions for quick lookup: {(habit_id, date_group_str): completions}
    completions_map: Dict[tuple[int, str], int] = {}
    for res in log_results:
        completions_map[(res.habit_id, str(res.date_group))] = res.completions

    for habit_obj in user_habits:
        data_points = []
        for label_date_str in labels:
            key_to_check_date_group = "" # This will be the string representation of the date group
            # Convert label_date_str (from chart labels) to the format used in date_group (from query)
            if time_period.lower() == "day": # Label: HH:00, Key: YYYY-MM-DD HH:00:00
                key_to_check_date_group = f"{start_date.strftime('%Y-%m-%d')} {label_date_str}:00"
            elif time_period.lower() == "week": # Label: Mon DD, Key: YYYY-MM-DD
                parsed_label_date = datetime.strptime(f"{start_date.year} {label_date_str}", f"%Y {date_format_str}").date()
                key_to_check_date_group = str(parsed_label_date)
            elif time_period.lower() == "month": # Label: Mon DD, Key: YYYY-MM-DD
                # Assuming labels are generated for the start_date's month
                parsed_label_date = datetime.strptime(f"{start_date.year}-{start_date.month:02d}-{label_date_str.split(' ')[1]}", "%Y-%m-%d").date()
                key_to_check_date_group = str(parsed_label_date)
            elif time_period.lower() == "year": # Label: Mon (e.g. Jan, Feb), Key: YYYY-MM
                month_num = datetime.strptime(label_date_str, "%b").month
                key_to_check_date_group = f"{start_date.year}-{month_num:02d}"
            else: # Default to month view, key is YYYY-MM-DD
                parsed_label_date = datetime.strptime(f"{start_date.year} {label_date_str}", f"%Y {date_format_str}").date()
                key_to_check_date_group = str(parsed_label_date)
            
            # Lookup in the prepared map
            completions_for_habit_date = completions_map.get((habit_obj.id, key_to_check_date_group), 0)
            data_points.append(completions_for_habit_date)

        datasets.append(ChartDataset(
            label=habit_obj.name,
            data=data_points,
            borderColor=f'rgb({(habit_obj.id * 30) % 255}, {(habit_obj.id * 50) % 255}, {(habit_obj.id * 70) % 255})',
            backgroundColor=f'rgba({(habit_obj.id * 30) % 255}, {(habit_obj.id * 50) % 255}, {(habit_obj.id * 70) % 255}, 0.5)'
        ))

    return HabitProgressData(labels=labels, datasets=datasets)

async def get_category_distribution_data(db: AsyncSession, user_id: int, time_period: str) -> CategoryDistributionData:
    start_date, end_date = get_date_range(time_period)

    stmt = (
        select(
            HabitCategory.name.label("category_name"),
            HabitCategory.color.label("category_color"),
            func.count(HabitTrackingLog.id).label("completions"),
        )
        .join(Habit, HabitCategory.id == Habit.category_id)
        .join(HabitTrackingLog, Habit.id == HabitTrackingLog.habit_id)
        .filter(
            HabitCategory.user_id == user_id,
            HabitTrackingLog.user_id == user_id,  # Ensure logs also belong to the user
            HabitTrackingLog.logged_datetime >= start_date,
            HabitTrackingLog.logged_datetime <= end_date
        )
        .group_by(HabitCategory.name, HabitCategory.color)
    )
    results_exec = await db.execute(stmt)
    results = results_exec.all()

    if not results:
        return CategoryDistributionData(labels=[], datasets=[PieChartDataset(data=[], backgroundColor=[])])

    labels = [r.category_name for r in results]
    data = [r.completions for r in results]
    # Use category colors if available, otherwise generate defaults
    background_colors = [
        r.category_color if r.category_color else f'rgba({(i * 60) % 255}, {(i * 90) % 255}, {(i * 120) % 255}, 0.7)' 
        for i, r in enumerate(results)
    ]
    border_colors = [bg.replace('0.7', '1') for bg in background_colors] # Make border opaque

    return CategoryDistributionData(
        labels=labels,
        datasets=[
            PieChartDataset(
                data=data,
                backgroundColor=background_colors,
                borderColor=border_colors
            )
        ]
    )

async def get_habit_performance_data(db: AsyncSession, user_id: int, time_period: str) -> List[HabitPerformanceItem]:
    start_date, end_date = get_date_range(time_period)
    
    # Fetch active habits for the user, preloading category for color access
    user_habits_stmt = select(Habit).options(selectinload(Habit.category)).filter(Habit.user_id == user_id)
    user_habits_exec = await db.execute(user_habits_stmt)
    user_habits = user_habits_exec.scalars().all()
    
    performance_items: List[HabitPerformanceItem] = []

    for habit_obj in user_habits:
        # TODO: Calculate actual performance percentage based on logs vs target/frequency
        # This is a complex calculation depending on habit type (daily, weekly, specific target)
        # For now, using a placeholder percentage.
        total_logs_stmt = select(func.count(HabitTrackingLog.id)).filter(
            HabitTrackingLog.habit_id == habit_obj.id,
            HabitTrackingLog.user_id == user_id,
            HabitTrackingLog.logged_datetime >= start_date,
            HabitTrackingLog.logged_datetime <= end_date
        )
        total_logs_result = await db.execute(total_logs_stmt)
        total_logs = total_logs_result.scalar_one_or_none() or 0
        
        # Placeholder percentage calculation (e.g., based on logs in period / (days in period * target_times_daily_equivalent))
        # This needs significant refinement based on habit.frequency_type and habit.target_times
        placeholder_percentage = (total_logs / 30) * 100 if time_period.lower() == "month" else (total_logs / 7) * 100 # very rough
        placeholder_percentage = min(round(placeholder_percentage, 0), 100) # Cap at 100

        performance_items.append(
            HabitPerformanceItem(
                id=str(habit_obj.id),
                name=habit_obj.name,
                percentage=placeholder_percentage, # Placeholder
                color=habit_obj.category.color if habit_obj.category and habit_obj.category.color else f'rgb({(habit_obj.id * 30) % 255}, {(habit_obj.id * 50) % 255}, {(habit_obj.id * 70) % 255})'
            )
        )
    return performance_items
