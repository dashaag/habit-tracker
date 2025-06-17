from typing import Annotated, Sequence
import datetime

from fastapi import Depends
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionContext # Assuming SessionContext is your AsyncSession
from app.models.habit import Habit, HabitCategory, HabitTrackingLog, FrequencyType
from app.schemas.habit import HabitStatistics # Import the statistics schema
from app.crud import crud_habit_tracking_log as crud_htl_sync # Import the synchronous crud instance
# We will define Pydantic schemas for create/update operations later
# from app.schemas.habit import HabitCreate, HabitUpdate, HabitCategoryCreate, HabitCategoryUpdate, HabitTrackingLogCreate, HabitTrackingLogUpdate

# --- HabitCategory CRUD --- #
class HabitCategoryRepository:
    def __init__(self, session: SessionContext):
        self.session = session

    async def create_habit_category(self, user_id: int, name: str, color: str | None = None) -> HabitCategory:
        db_category = HabitCategory(user_id=user_id, name=name, color=color)
        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)
        return db_category

    async def get_habit_category_by_id(self, category_id: int, user_id: int) -> HabitCategory | None:
        query = select(HabitCategory).filter(HabitCategory.id == category_id, HabitCategory.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_habit_categories_by_user_id(self, user_id: int) -> Sequence[HabitCategory]:
        query = select(HabitCategory).filter(HabitCategory.user_id == user_id).order_by(HabitCategory.name)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_habit_category_by_name(self, user_id: int, name: str) -> HabitCategory | None:
        query = select(HabitCategory).filter(HabitCategory.user_id == user_id, HabitCategory.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_habit_category(self, category_id: int, user_id: int, name: str | None = None, color: str | None = None) -> HabitCategory | None:
        category = await self.get_habit_category_by_id(category_id=category_id, user_id=user_id)
        if not category:
            return None
        if name is not None:
            category.name = name
        if icon is not None:
            category.icon = icon
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def delete_habit_category(self, category_id: int, user_id: int) -> bool:
        query = delete(HabitCategory).filter(HabitCategory.id == category_id, HabitCategory.user_id == user_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

# --- Habit CRUD --- #
class HabitRepository:
    def __init__(self, session: SessionContext):
        self.session = session

    async def create_habit(self, user_id: int, name: str, icon: str | None = None, 
                           frequency_type: FrequencyType = FrequencyType.DAILY, 
                           target_times: int | None = None, # Updated
                           days_of_week: str | None = None, # Added
                           times_of_day: str | None = None, # Added
                           reminder_on: bool = False, # Updated
                           streak_goal: int | None = None, category_id: int | None = None) -> Habit:
        db_habit = Habit(
            user_id=user_id, name=name, icon=icon, frequency_type=frequency_type,
            target_times=target_times, days_of_week=days_of_week, times_of_day=times_of_day, 
            reminder_on=reminder_on, streak_goal=streak_goal, category_id=category_id
        )
        self.session.add(db_habit)
        await self.session.commit()
        await self.session.refresh(db_habit)
        return db_habit

    async def get_habit_by_id(self, habit_id: int, user_id: int) -> Habit | None:
        query = select(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_habits_by_user_id(self, user_id: int, category_id: int | None = None) -> Sequence[Habit]:
        query = (
            select(Habit)
            .options(selectinload(Habit.tracking_logs), selectinload(Habit.category))
            .filter(Habit.user_id == user_id)
        )
        if category_id is not None:
            query = query.filter(Habit.category_id == category_id)
        query = query.order_by(Habit.name)
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def update_habit(self, habit_id: int, user_id: int, values_to_update: dict) -> Habit | None:
        # Ensure user_id is not in values_to_update to prevent changing ownership
        values_to_update.pop('user_id', None) 
        if not values_to_update:
            # If nothing to update, fetch and return the habit
            return await self.get_habit_by_id(habit_id=habit_id, user_id=user_id)
            
        stmt = update(Habit).where(Habit.id == habit_id, Habit.user_id == user_id).values(**values_to_update).returning(Habit)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete_habit(self, habit_id: int, user_id: int) -> bool:
        # First, delete all tracking logs associated with this habit and user
        delete_logs_query = delete(HabitTrackingLog).filter(
            HabitTrackingLog.habit_id == habit_id,
            HabitTrackingLog.user_id == user_id  # Ensure user owns the logs via habit's user_id implicitly or directly if log has user_id
        )
        await self.session.execute(delete_logs_query)
        # It's generally good to commit this separately or ensure the transactionality covers both, 
        # but for simplicity here, we'll let the habit deletion commit handle both if it's part of the same transaction scope.
        # However, if the habit deletion fails after logs are deleted, logs would remain deleted.
        # For robust transaction, consider a single commit after both operations if possible or handle rollbacks.

        # Then, delete the habit itself
        delete_habit_query = delete(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id)
        result = await self.session.execute(delete_habit_query)
        await self.session.commit() # Commit after both operations
        return result.rowcount > 0

# --- HabitTrackingLog CRUD --- #
class HabitTrackingLogRepository:
    def __init__(self, session: SessionContext):
        self.session = session

    async def create_tracking_log(self, habit_id: int, user_id: int, logged_datetime: datetime.datetime,
                                  completed: bool = False, progress: int | None = None) -> HabitTrackingLog:
        db_log = HabitTrackingLog(
            habit_id=habit_id,
            user_id=user_id,
            logged_datetime=logged_datetime,
            completed=completed,
            progress=progress
        )
        self.session.add(db_log)
        await self.session.commit()
        await self.session.refresh(db_log)
        return db_log

    async def get_tracking_log_by_id(self, log_id: int) -> HabitTrackingLog | None:
        # Add user_id check via join with Habit if logs are user-specific
        query = select(HabitTrackingLog).filter(HabitTrackingLog.id == log_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_tracking_logs_by_habit_id(self, habit_id: int, 
                                            start_date: datetime.date | None = None, 
                                            end_date: datetime.date | None = None) -> Sequence[HabitTrackingLog]:
        query = select(HabitTrackingLog).filter(HabitTrackingLog.habit_id == habit_id)
        if start_date:
            query = query.filter(HabitTrackingLog.logged_datetime >= datetime.datetime.combine(start_date, datetime.time.min))
        if end_date:
            query = query.filter(HabitTrackingLog.logged_datetime <= datetime.datetime.combine(end_date, datetime.time.max))
        query = query.order_by(HabitTrackingLog.logged_datetime.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_tracking_log(self, log_id: int, completed: bool | None = None, progress: int | None = None) -> HabitTrackingLog | None:
        log_entry = await self.get_tracking_log_by_id(log_id=log_id)
        if not log_entry:
            return None
        if completed is not None:
            log_entry.completed = completed
        if progress is not None:
            log_entry.progress = progress
        await self.session.commit()
        await self.session.refresh(log_entry)
        return log_entry

    async def delete_tracking_log(self, log_id: int) -> bool:
        query = delete(HabitTrackingLog).filter(HabitTrackingLog.id == log_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def get_habit_statistics(
        self,
        habit_id: int,
        user_id: int, # Ensure user_id is used for authorization checks before calling this
        days: int = 30
    ) -> HabitStatistics:
        # This method calls the synchronous CRUD function using run_sync
        # The actual database query logic is in crud_habit_tracking_log.py
        
        # Define a synchronous function to be run by run_sync
        def _get_stats_sync(sync_session):
            # Note: We are accessing habit_tracking_log attribute from the imported crud_htl_sync module
            return crud_htl_sync.habit_tracking_log.get_statistics_by_habit(
                db=sync_session,
                habit_id=habit_id,
                user_id=user_id, # Passed for the sync function's logic
                days=days
            )
        
        # Execute the synchronous function in a way that's compatible with AsyncSession
        statistics_data = await self.session.run_sync(_get_stats_sync)
        return statistics_data


HabitCategoryRepositoryDependency = Annotated[HabitCategoryRepository, Depends(HabitCategoryRepository)]
HabitRepositoryDependency = Annotated[HabitRepository, Depends(HabitRepository)]
HabitTrackingLogRepositoryDependency = Annotated[HabitTrackingLogRepository, Depends(HabitTrackingLogRepository)]
