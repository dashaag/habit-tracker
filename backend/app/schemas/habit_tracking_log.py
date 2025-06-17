from pydantic import BaseModel, Field
import datetime
from typing import Optional

# Shared properties
class HabitTrackingLogBase(BaseModel):
    # Frontend sends 'logged_at', backend model uses 'logged_datetime'
    # The alias 'logged_at' allows Pydantic to map the incoming 'logged_at' field 
    # to the 'logged_datetime' attribute of the model.
    logged_datetime: datetime.datetime = Field(..., alias='logged_at')
    completed: Optional[bool] = True
    progress: Optional[int] = None
    notes: Optional[str] = None

# Properties to receive on item creation
class HabitTrackingLogCreate(HabitTrackingLogBase):
    habit_id: int
    # user_id will be injected from the current user in the controller

    class Config:
        # When True, Pydantic will attempt to populate model fields using the field's alias 
        # if the original field name is not found in the input data. This is crucial for the alias to work.
        populate_by_name = True # For Pydantic V2. For V1, use allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "habit_id": 1,
                "logged_at": "2025-06-15T19:24:17Z", # Example using current time from prompt
                "completed": True,
                "progress": None,
                "notes": "First log!"
            }
        }

# Properties to receive on item update
class HabitTrackingLogUpdate(HabitTrackingLogBase):
    # If you allow updating logged_datetime, the alias defined in HabitTrackingLogBase will apply.
    # You can also override fields here if needed, for example, to make them all optional for PATCH.
    # Example: logged_datetime: Optional[datetime.datetime] = Field(None, alias='logged_at')
    # For now, assume all fields from base are updatable as is.
    pass

# Properties shared by models stored in DB
class HabitTrackingLogInDBBase(HabitTrackingLogBase):
    id: int
    habit_id: int
    user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True # Pydantic V2 (replaces orm_mode for V1). Allows creating model from ORM object.

# Additional properties to return to client (usually the same as InDBBase or a subset)
class HabitTrackingLog(HabitTrackingLogInDBBase):
    pass

# Additional properties stored in DB (often same as HabitTrackingLog, but can differ if needed)
class HabitTrackingLogInDB(HabitTrackingLogInDBBase):
    pass
