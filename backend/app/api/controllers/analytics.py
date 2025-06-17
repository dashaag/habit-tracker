from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_db_session
from typing import Optional
from app.schemas.user import User
from app.schemas.analytics import AnalyticsResponse, AnalyticsFilters
from app.crud import crud_analytics

router = APIRouter()

@router.get("/", response_model=AnalyticsResponse)
async def get_analytics_data(
    *, # Ensures all subsequent parameters are keyword-only
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    filters: AnalyticsFilters = Depends() # Injects query params: time_period, habit_id
):
    """
    Retrieve aggregated analytics data for the current user.

    - **time_period**: Filter data by 'Day', 'Week', 'Month', 'Year'. Defaults to 'Month'.
    - **habit_id**: Optional. Filter data for a specific habit ID.
    """
    user_id = current_user.id
    time_period = filters.time_period
    # Convert habit_id from string (if provided via query) to int, or keep as None
    habit_id_int: Optional[int] = None
    if filters.habit_id is not None:
        try:
            habit_id_int = int(filters.habit_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid habit_id format. Must be an integer."
            ) from exc

    summary_stats = await crud_analytics.get_summary_stats(
        db=db, user_id=user_id, time_period=time_period, habit_id_filter=habit_id_int
    )
    habit_progress = await crud_analytics.get_habit_progress_data(
        db=db, user_id=user_id, time_period=time_period, habit_id_filter=habit_id_int
    )
    category_distribution = await crud_analytics.get_category_distribution_data(
        db=db, user_id=user_id, time_period=time_period
    )
    habit_performance = await crud_analytics.get_habit_performance_data(
        db=db, user_id=user_id, time_period=time_period
    )

    return AnalyticsResponse(
        summary_stats=summary_stats,
        habit_progress=habit_progress,
        category_distribution=category_distribution,
        habit_performance=habit_performance,
    )
