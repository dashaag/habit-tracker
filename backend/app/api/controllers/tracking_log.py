from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any

from app import schemas, models
# Import repository dependencies
from app.crud.habit import HabitRepositoryDependency, HabitTrackingLogRepositoryDependency
from app.api.dependencies import get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.HabitTrackingLog)
async def create_habit_tracking_log(
    *,
    log_in: schemas.HabitTrackingLogCreate,
    habit_repo: HabitRepositoryDependency,
    tracking_log_repo: HabitTrackingLogRepositoryDependency,
    current_user: models.User = Depends(get_current_active_user)
) -> Any:
    """
    Create new habit tracking log.
    `user_id` is automatically associated with the current authenticated user.
    """
    # Check if the habit exists and belongs to the current user
    habit = await habit_repo.get_habit_by_id(habit_id=log_in.habit_id, user_id=current_user.id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {log_in.habit_id} not found or you do not have permission."
        )

    log = await tracking_log_repo.create_tracking_log(
        habit_id=log_in.habit_id,
        user_id=current_user.id,
        logged_datetime=log_in.logged_datetime
    )
    return log

@router.get("/habit/{habit_id}", response_model=List[schemas.HabitTrackingLog])
async def read_habit_tracking_logs_for_habit(
    *,
    habit_id: int,
    habit_repo: HabitRepositoryDependency,
    tracking_log_repo: HabitTrackingLogRepositoryDependency,
    current_user: models.User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve tracking logs for a specific habit of the current user.
    """
    habit = await habit_repo.get_habit_by_id(habit_id=habit_id, user_id=current_user.id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with id {habit_id} not found or you do not have permission."
        )
    logs = await tracking_log_repo.get_tracking_logs_by_habit_id(habit_id=habit_id)
    return logs

@router.get("/{log_id}", response_model=schemas.HabitTrackingLog)
async def read_habit_tracking_log(
    *,
    log_id: int,
    habit_repo: HabitRepositoryDependency,
    tracking_log_repo: HabitTrackingLogRepositoryDependency,
    current_user: models.User = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific habit tracking log by ID.
    """
    log = await tracking_log_repo.get_tracking_log_by_id(log_id=log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit log with id {log_id} not found."
        )
    
    # Verify the user has permission to view this log by checking habit ownership
    habit = await habit_repo.get_habit_by_id(habit_id=log.habit_id, user_id=current_user.id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this log."
        )
        
    return log

@router.delete("/{log_id}", response_model=schemas.HabitTrackingLog)
async def delete_habit_tracking_log(
    *,
    log_id: int,
    habit_repo: HabitRepositoryDependency,
    tracking_log_repo: HabitTrackingLogRepositoryDependency,
    current_user: models.User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a habit tracking log.
    """
    log_to_delete = await tracking_log_repo.get_tracking_log_by_id(log_id=log_id)
    if not log_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit log not found.")

    # Verify the user has permission to delete this log by checking habit ownership
    habit = await habit_repo.get_habit_by_id(habit_id=log_to_delete.habit_id, user_id=current_user.id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this log."
        )

    await tracking_log_repo.delete_tracking_log(log_id=log_id)
    return log_to_delete
