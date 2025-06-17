import datetime
from typing import Optional, List

from pydantic import Field # Added import for Field
from app.schemas.base import CustomBaseModel, IdSchema, TimestampSchema
from app.models.habit import FrequencyType # Enum for frequency_type

# --- HabitCategory Schemas --- #
class HabitCategoryBase(CustomBaseModel):
    name: str
    color: Optional[str] = None

class HabitCategoryCreate(HabitCategoryBase):
    pass

class HabitCategoryUpdate(CustomBaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class HabitCategory(HabitCategoryBase, IdSchema, TimestampSchema):
    user_id: int

    class Config:
        from_attributes = True

# --- Habit Schemas --- #
class HabitBase(CustomBaseModel):
    name: str
    icon: Optional[str] = None
    frequency_type: FrequencyType = FrequencyType.DAILY
    target_times: Optional[int] = None # Updated: Now optional, default handled by model or logic
    days_of_week: Optional[str] = None # Added: For weekly habits, JSON string array of day numbers
    times_of_day: Optional[str] = None # Added: For daily habits, JSON string array of times
    reminder_on: bool = False # Updated: Default to False
    streak_goal: Optional[int] = None
    category_id: Optional[int] = None

class HabitCreate(HabitBase):
    pass

class HabitUpdate(CustomBaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    frequency_type: Optional[FrequencyType] = None
    target_times: Optional[int] = None
    days_of_week: Optional[str] = None # Added
    times_of_day: Optional[str] = None # Added
    reminder_on: Optional[bool] = None
    streak_goal: Optional[int] = None
    category_id: Optional[int] = None

class Habit(HabitBase, IdSchema, TimestampSchema):
    user_id: int
    category: Optional[HabitCategory] = None  # Nested category info
    tracking_logs: List['HabitTrackingLog'] = []

# --- HabitTrackingLog Schemas --- #
class HabitTrackingLogBase(CustomBaseModel):
    logged_datetime: datetime.datetime = Field(..., alias="logged_at")
    completed: bool = False
    progress: Optional[int] = None

class HabitTrackingLogCreate(HabitTrackingLogBase):
    habit_id: int

class HabitTrackingLogUpdate(CustomBaseModel):
    logged_datetime: Optional[datetime.datetime] = None
    completed: Optional[bool] = None
    progress: Optional[int] = None

class HabitTrackingLog(HabitTrackingLogBase, IdSchema, TimestampSchema):
    habit_id: int

    class Config:
        from_attributes = True


# --- Habit Statistics Schemas --- #
class HabitDailyStat(CustomBaseModel):
    date: datetime.date
    value: int # Could be count of logs, or sum of progress if applicable

class HabitStatistics(CustomBaseModel):
    total_completions: int
    # avg_completion_percentage: float # This might be better calculated on frontend based on current target
    daily_stats: List[HabitDailyStat]
    # Potentially add start_date, end_date if needed for context

