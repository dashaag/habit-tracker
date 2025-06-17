from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any

# --- Schemas for Chart Datasets ---
class ChartDataset(BaseModel):
    label: str
    data: List[Union[int, float]]
    borderColor: Optional[str] = None
    backgroundColor: Optional[str] = None
    fill: Optional[bool] = None # For area charts, if needed

class PieChartDataset(BaseModel):
    label: Optional[str] = None # Often not needed for single dataset pie charts
    data: List[Union[int, float]]
    backgroundColor: List[str]
    borderColor: Optional[List[str]] = None
    borderWidth: Optional[int] = 1

# --- Schemas for Analytics Page Sections ---
class SummaryStats(BaseModel):
    total_completions: int
    day_streak: int # Note: Complex to calculate accurately, may be simplified
    avg_per_habit: float
    active_habits: int

class HabitProgressData(BaseModel):
    labels: List[str] # e.g., dates or time periods
    datasets: List[ChartDataset]

class CategoryDistributionData(BaseModel):
    labels: List[str] # Category names
    datasets: List[PieChartDataset]

class HabitPerformanceItem(BaseModel):
    id: str # Habit ID
    name: str
    percentage: float
    color: Optional[str] = None # Frontend might handle colors
    # Optional: raw counts for more details
    # completions: int
    # target: int 

# --- Main Analytics Response Schema ---
class AnalyticsResponse(BaseModel):
    summary_stats: SummaryStats
    habit_progress: HabitProgressData
    category_distribution: CategoryDistributionData
    habit_performance: List[HabitPerformanceItem]

# --- Request Query Parameters Schema (Optional but good practice) ---
class AnalyticsFilters(BaseModel):
    time_period: str = "Month" # e.g., Day, Week, Month, Year
    habit_id: Optional[str] = None # For filtering by a specific habit, 'all' or None for all habits
    # category_id: Optional[str] = None # Future: filter by category
