from pydantic import BaseModel, ConfigDict
import datetime

class CustomBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class IdSchema(CustomBaseModel):
    id: int

class TimestampSchema(CustomBaseModel):
    created_at: datetime.datetime
    updated_at: datetime.datetime
