from sqlalchemy import Column, Integer, DateTime, ForeignKey, func, String
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    logged_at = Column(DateTime, nullable=False)
    notes = Column(String(255), nullable=True) # Optional: if users can add notes to a log

    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    habit = relationship("Habit", back_populates="logs")
    user = relationship("User", back_populates="habit_logs")
