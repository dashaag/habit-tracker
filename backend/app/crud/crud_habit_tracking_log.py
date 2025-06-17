from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date as SQLDate # Added cast and SQLDate
from typing import List, Optional
import datetime

from app.models.habit import HabitTrackingLog # Corrected import path
from app.schemas.habit_tracking_log import HabitTrackingLogCreate, HabitTrackingLogUpdate
from app.schemas.habit import HabitStatistics, HabitDailyStat # Added statistics schemas

class CRUDHabitTrackingLog:
    def get(self, db: Session, id: int, user_id: int) -> Optional[HabitTrackingLog]:
        return db.query(HabitTrackingLog).filter(HabitTrackingLog.id == id, HabitTrackingLog.user_id == user_id).first()

    def get_multi_by_habit(self, db: Session, *, habit_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[HabitTrackingLog]:
        return (
            db.query(HabitTrackingLog)
            .filter(HabitTrackingLog.habit_id == habit_id, HabitTrackingLog.user_id == user_id)
            .order_by(HabitTrackingLog.logged_datetime.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_multi_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[HabitTrackingLog]:
        return (
            db.query(HabitTrackingLog)
            .filter(HabitTrackingLog.user_id == user_id)
            .order_by(HabitTrackingLog.logged_datetime.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_owner(self, db: Session, *, obj_in: HabitTrackingLogCreate, user_id: int) -> HabitTrackingLog:
        db_obj = HabitTrackingLog(
            **obj_in.model_dump(exclude_unset=True), # Pydantic V2, use .dict() for V1
            user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: HabitTrackingLog, obj_in: HabitTrackingLogUpdate, user_id: int) -> Optional[HabitTrackingLog]:
        if db_obj.user_id != user_id:
            return None # Or raise an exception for unauthorized access
        
        update_data = obj_in.model_dump(exclude_unset=True) # Pydantic V2, use .dict() for V1
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int, user_id: int) -> Optional[HabitTrackingLog]:
        obj = db.query(HabitTrackingLog).filter(HabitTrackingLog.id == id, HabitTrackingLog.user_id == user_id).first()
        if not obj:
            return None
        db.delete(obj)
        db.commit()
        return obj

    def get_statistics_by_habit(
        self,
        db: Session,
        *,
        habit_id: int,
        user_id: int,
        days: int = 30
    ) -> HabitStatistics:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days -1) # -1 because we want to include today in the 30 days

        # Query to get daily completion counts
        daily_counts_query = (
            db.query(
                cast(HabitTrackingLog.logged_datetime, SQLDate).label("log_date"),
                func.count(HabitTrackingLog.id).label("count")
            )
            .filter(
                HabitTrackingLog.habit_id == habit_id,
                HabitTrackingLog.user_id == user_id,
                cast(HabitTrackingLog.logged_datetime, SQLDate) >= start_date,
                cast(HabitTrackingLog.logged_datetime, SQLDate) <= end_date
            )
            .group_by(cast(HabitTrackingLog.logged_datetime, SQLDate))
            .order_by(cast(HabitTrackingLog.logged_datetime, SQLDate))
            .all()
        )

        # Process results into a dictionary for easy lookup
        logs_by_date = {log.log_date: log.count for log in daily_counts_query}

        daily_stats_list: List[HabitDailyStat] = []
        total_completions = 0

        # Generate stats for each day in the period, filling with 0 if no logs
        for i in range(days):
            current_date = start_date + datetime.timedelta(days=i)
            count_for_day = logs_by_date.get(current_date, 0)
            daily_stats_list.append(HabitDailyStat(date=current_date, value=count_for_day))
            total_completions += count_for_day
        
        return HabitStatistics(
            total_completions=total_completions,
            daily_stats=daily_stats_list
        )

habit_tracking_log = CRUDHabitTrackingLog()
