import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies import get_current_active_user
from app.crud.habit import (
    HabitCategoryRepositoryDependency,
    HabitRepositoryDependency,
    HabitTrackingLogRepositoryDependency,
)
from app.schemas import (
    Habit,
    HabitCategory,
    HabitCategoryCreate,
    HabitCategoryUpdate,
    HabitCreate,
    HabitUpdate,
    HabitTrackingLog,
    HabitTrackingLogCreate,
    HabitTrackingLogUpdate,
    HabitStatistics, # Added for response model
    User,
)

router = APIRouter()

# --- Habit Category Endpoints --- #

@router.post("/categories", response_model=HabitCategory, status_code=status.HTTP_201_CREATED)
async def create_habit_category(
    category_in: HabitCategoryCreate,
    category_repo: HabitCategoryRepositoryDependency,
    current_user: User = Depends(get_current_active_user),
):
    return await category_repo.create_habit_category(user_id=current_user.id, name=category_in.name, color=category_in.color)

@router.get("/categories", response_model=List[HabitCategory])
async def get_user_habit_categories(
    category_repo: HabitCategoryRepositoryDependency,
    current_user: User = Depends(get_current_active_user),
):
    return await category_repo.get_habit_categories_by_user_id(user_id=current_user.id)

@router.put("/categories/{category_id}", response_model=HabitCategory)
async def update_habit_category(
    category_id: int,
    category_in: HabitCategoryUpdate,
    category_repo: HabitCategoryRepositoryDependency,
    current_user: User = Depends(get_current_active_user),
):
    updated_category = await category_repo.update_habit_category(
        category_id=category_id,
        user_id=current_user.id,
        name=category_in.name,
        color=category_in.color,
    )
    if not updated_category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Habit category not found or not owned by user")
    return updated_category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit_category(
    category_id: int,
    category_repo: HabitCategoryRepositoryDependency,
    current_user: User = Depends(get_current_active_user),
):
    deleted = await category_repo.delete_habit_category(
        category_id=category_id, user_id=current_user.id
    )
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Habit category not found or not owned by user")
    return

# --- Habit Endpoints --- #

@router.post("", response_model=Habit, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit_in: HabitCreate,
    habit_repo: HabitRepositoryDependency,
    current_user: User = Depends(get_current_active_user),
):
    # Use model_dump to pass all validated data from the Pydantic model
    # to the repository function. This is more robust and less error-prone.
    return await habit_repo.create_habit(user_id=current_user.id, **habit_in.model_dump())

@router.get("", response_model=List[Habit])
async def get_user_habits(
    habit_repo: HabitRepositoryDependency, current_user: User = Depends(get_current_active_user)
):
    return await habit_repo.get_habits_by_user_id(user_id=current_user.id)

@router.get("/{habit_id}", response_model=Habit)
async def get_habit(
    habit_id: int, habit_repo: HabitRepositoryDependency, current_user: User = Depends(get_current_active_user)
):
    habit = await habit_repo.get_habit_by_id(habit_id=habit_id, user_id=current_user.id)
    if not habit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Habit not found")
    return habit

@router.put("/{habit_id}", response_model=Habit)
async def update_habit(
    habit_id: int,
    habit_in: HabitUpdate,
    habit_repo: HabitRepositoryDependency,
    current_user: User = Depends(get_current_active_user),
):
    habit = await habit_repo.get_habit_by_id(habit_id=habit_id, user_id=current_user.id)
    if not habit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Habit not found")
    return await habit_repo.update_habit(habit_id=habit_id, user_id=current_user.id, values_to_update=habit_in.model_dump(exclude_none=True))

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: int, habit_repo: HabitRepositoryDependency, current_user: User = Depends(get_current_active_user)
):
    habit = await habit_repo.get_habit_by_id(habit_id=habit_id, user_id=current_user.id)
    if not habit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Habit not found")
    await habit_repo.delete_habit(habit_id=habit_id, user_id=current_user.id)
    return

@router.get("/{habit_id}/statistics", response_model=HabitStatistics)
async def get_habit_statistics(
    habit_id: int,
    habit_repo: HabitRepositoryDependency,
    log_repo: HabitTrackingLogRepositoryDependency,
    days: int = Query(30, ge=1, le=365), # Default 30 days, min 1, max 365
    current_user: User = Depends(get_current_active_user),
):
    habit = await habit_repo.get_habit_by_id(habit_id=habit_id, user_id=current_user.id)
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found or not owned by user")
    
    statistics = await log_repo.get_habit_statistics(
        habit_id=habit_id,
        user_id=current_user.id,
        days=days
    )
    return statistics

# --- Habit Tracking Log Endpoints --- #

@router.post("/{habit_id}/logs", response_model=HabitTrackingLog, status_code=status.HTTP_201_CREATED)
async def create_habit_log(
    habit_id: int,
    log_in: HabitTrackingLogCreate,
    habit_repo: HabitRepositoryDependency,
    log_repo: HabitTrackingLogRepositoryDependency,
    current_user: User = Depends(get_current_active_user),
):
    habit = await habit_repo.get_habit_by_id(habit_id=habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Habit not found")
    if log_in.habit_id != habit_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Habit ID mismatch")
    return await log_repo.create_log(log_data=log_in)

@router.get("/{habit_id}/logs", response_model=List[HabitTrackingLog])
async def get_habit_logs(
    habit_id: int,
    log_repo: HabitTrackingLogRepositoryDependency,
    habit_repo: HabitRepositoryDependency,
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
):
    habit = await habit_repo.get_habit_by_id(habit_id=habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Habit not found")
    return await log_repo.get_logs_by_habit(habit_id=habit_id, start_date=start_date, end_date=end_date)

@router.put("/logs/{log_id}", response_model=HabitTrackingLog)
async def update_habit_log(
    log_id: int,
    log_in: HabitTrackingLogUpdate,
    log_repo: HabitTrackingLogRepositoryDependency,
    habit_repo: HabitRepositoryDependency,
    current_user: User = Depends(get_current_active_user),
):
    log = await log_repo.get_log_by_id(log_id=log_id)
    if not log:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Log not found")
    habit = await habit_repo.get_habit_by_id(habit_id=log.habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    return await log_repo.update_log(log_id=log_id, date=log_in.date, habit_id=log_in.habit_id, is_completed=log_in.is_completed)

@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit_log(
    log_id: int,
    log_repo: HabitTrackingLogRepositoryDependency,
    habit_repo: HabitRepositoryDependency,
    current_user: User = Depends(get_current_active_user),
):
    log = await log_repo.get_log_by_id(log_id=log_id)
    if not log:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Log not found")
    habit = await habit_repo.get_habit_by_id(habit_id=log.habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    await log_repo.delete_log(log_id=log_id)
    return
