import enum
import datetime
from sqlalchemy import String, Integer, ForeignKey, Time, Boolean, Enum as SQLAlchemyEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import IdBase, TimestampMixin # Use IdBase and TimestampMixin

class FrequencyType(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"

class HabitCategory(IdBase, TimestampMixin):
    __tablename__ = "habit_categories"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user = relationship("User", back_populates="habit_categories")
    habits = relationship("Habit", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HabitCategory {self.name}>"

class Habit(IdBase, TimestampMixin):
    __tablename__ = "habits"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    frequency_type: Mapped[FrequencyType] = mapped_column(SQLAlchemyEnum(FrequencyType), default=FrequencyType.DAILY, nullable=False)
    target_times: Mapped[int | None] = mapped_column(Integer, nullable=True)
    days_of_week: Mapped[str] = mapped_column(String, default="[]", nullable=True)
    times_of_day: Mapped[str] = mapped_column(String, default="[]", nullable=True)
    reminder_on: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    streak_goal: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("habit_categories.id"), nullable=True)

    user = relationship("User", back_populates="habits")
    category = relationship("HabitCategory", back_populates="habits", lazy="joined")
    tracking_logs = relationship("HabitTrackingLog", back_populates="habit", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self):
        return f"<Habit {self.name}>"

class HabitTrackingLog(IdBase, TimestampMixin):
    __tablename__ = "habit_tracking_logs"

    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey("habits.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    # logged_datetime is distinct from created_at (when the log entry was made)
    # and represents the actual time the habit was performed or intended to be performed.
    logged_datetime: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    progress: Mapped[int | None] = mapped_column(Integer, nullable=True) # Optional, e.g., for habits like 'read 50 pages'

    habit = relationship("Habit", back_populates="tracking_logs", lazy="joined")
    user = relationship("User", back_populates="habit_tracking_logs")

    def __repr__(self):
        return f"<HabitTrackingLog habit_id={self.habit_id} at {self.logged_datetime}>"
