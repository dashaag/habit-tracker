import React, { useState, useEffect, useMemo } from 'react';
import api from '../services/api';
import './AnalyticsPage.scss';
import {
  ResponsiveContainer,
  LineChart,
  BarChart,
  PieChart,
  Line as RechartsLine,
  Bar as RechartsBar,
  Pie as RechartsPie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
} from 'recharts';

// Default colors for Pie chart if not provided by backend
const DEFAULT_PIE_COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82Ca9D'];

const AnalyticsPage = () => {
  // State for filters
  const [filters, setFilters] = useState({
    timePeriod: 'Month',
    selectedHabit: 'all',
    chartType: 'Line', // For Habit Progress chart
  });

  // State for data
  const [habitsList, setHabitsList] = useState([]);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch habits for the filter dropdown
  useEffect(() => {
    let isMounted = true;
    const fetchHabits = async () => {
      try {
        const response = await api.get('/habits');
        if (isMounted) {
          setHabitsList([{ id: 'all', name: 'All Habits' }, ...response.data]);
        }
      } catch (err) {
        console.error('Failed to fetch habits:', err);
      }
    };
    fetchHabits();
    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch analytics data when filters change
  useEffect(() => {
    let isActive = true;
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = {
          time_period: filters.timePeriod,
        };
        if (filters.selectedHabit && filters.selectedHabit !== 'all') {
          params.habit_id = filters.selectedHabit;
        }
        const response = await api.get('/api/v1/analytics/', { params });
        if (isActive) {
          setAnalyticsData(response.data);
        }
      } catch (err) {
        console.error('Failed to load analytics data:', err);
        if (isActive) {
          setError(`Failed to load analytics. ${err.response?.data?.detail || err.message}`);
          setAnalyticsData(null);
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    };
    fetchAnalytics();
    return () => {
      isActive = false;
    };
  }, [filters.timePeriod, filters.selectedHabit]);

  const handleFilterChange = (filterName, value) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      [filterName]: value,
    }));
  };

  // Memoized data transformations for Recharts
  const habitProgressChartData = useMemo(() => {
    const rawData = analyticsData?.habit_progress;
    if (!rawData || !rawData.labels || !rawData.labels.length || !rawData.datasets || !rawData.datasets.length) {
      return [];
    }

    const transformedData = rawData.labels.map((label, index) => {
      const dataPoint = { name: label };
      rawData.datasets.forEach(dataset => {
        dataPoint[dataset.label] = dataset.data[index];
      });
      return dataPoint;
    });
    return transformedData;
  }, [analyticsData?.habit_progress]);

  const habitProgressDatasets = useMemo(() => {
    return analyticsData?.habit_progress?.datasets || [];
  }, [analyticsData?.habit_progress]);

  const categoryDistributionChartData = useMemo(() => {
    const rawData = analyticsData?.category_distribution;
    if (!rawData || !rawData.labels || !rawData.labels.length || !rawData.datasets || !rawData.datasets.length || !rawData.datasets[0].data) {
      return [];
    }
    return rawData.labels.map((label, index) => ({
      name: label,
      value: rawData.datasets[0].data[index],
      // Use backend-provided colors if available, otherwise fallback to default
      fill: rawData.datasets[0].backgroundColor?.[index] || DEFAULT_PIE_COLORS[index % DEFAULT_PIE_COLORS.length],
    }));
  }, [analyticsData?.category_distribution]);

  const summaryStats = analyticsData?.summary_stats;
  const habitPerformance = analyticsData?.habit_performance || [];

  if (loading && !analyticsData) {
    return <div className="analytics-page-loading">Loading analytics dashboard...</div>;
  }

  return (
    <div className="analytics-page">
      <div className='analytics-content'>
      <header className="analytics-header">
        <h1>Habit Analytics</h1>
        <p>Gain insights into your habits and track your journey.</p>
      </header>

      <section className="filters-section card">
        <div className="filter-group">
          <label htmlFor="time-period-filter">Time Period</label>
          <select id="time-period-filter" value={filters.timePeriod} onChange={(e) => handleFilterChange('timePeriod', e.target.value)}>
            <option value="Day">Day</option>
            <option value="Week">Week</option>
            <option value="Month">Month</option>
            <option value="Year">Year</option>
          </select>
        </div>
        <div className="filter-group">
          <label htmlFor="habit-filter">Habit</label>
          <select id="habit-filter" value={filters.selectedHabit} onChange={(e) => handleFilterChange('selectedHabit', e.target.value)} disabled={!habitsList.length}>
            {habitsList.length > 0 ? (
              habitsList.map((habit) => (
                <option key={habit.id} value={habit.id}>{habit.name}</option>
              ))
            ) : (
              <option value="" disabled>Loading habits...</option>
            )}
          </select>
        </div>
        <div className="filter-group">
          <label htmlFor="chart-type-filter">Progress Chart Type</label>
          <select id="chart-type-filter" value={filters.chartType} onChange={(e) => handleFilterChange('chartType', e.target.value)}>
            <option value="Line">Line</option>
            <option value="Bar">Bar</option>
          </select>
        </div>
      </section>

      {error && <div className="error-message card">{error}</div>}
      
      {summaryStats && !loading && (
        <section className="summary-stats-section">
          <div className="stat-card"><h3>Total Completions</h3><p>{summaryStats.total_completions ?? 'N/A'}</p></div>
          <div className="stat-card"><h3>Active Habits</h3><p>{summaryStats.active_habits ?? 'N/A'}</p></div>
        </section>
      )}

      <section className="charts-section">
        <div className="chart-container card">
          <h2>Habit Progress Over Time</h2>
          {loading && !habitProgressChartData.length ? (
            <div className="chart-placeholder">Loading chart...</div>
          ) : habitProgressChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              {filters.chartType === 'Line' ? (
                <LineChart data={habitProgressChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip itemStyle={{ fontSize: '12px' }} labelStyle={{ fontSize: '12px' }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  {habitProgressDatasets.map((dataset) => (
                    <RechartsLine key={dataset.label} type="monotone" dataKey={dataset.label} stroke={dataset.borderColor || '#8884d8'} activeDot={{ r: 8 }} />
                  ))}
                </LineChart>
              ) : (
                <BarChart data={habitProgressChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip itemStyle={{ fontSize: '12px' }} labelStyle={{ fontSize: '12px' }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  {habitProgressDatasets.map((dataset) => (
                    <RechartsBar key={dataset.label} dataKey={dataset.label} fill={dataset.backgroundColor || '#82ca9d'} />
                  ))}
                </BarChart>
              )}
            </ResponsiveContainer>
          ) : !loading ? (
            <div className="chart-placeholder">No progress data for selected filters.</div>
          ) : null}
        </div>

        <div className="chart-container card">
          <h2>Category Distribution</h2>
          {loading && !categoryDistributionChartData.length ? (
            <div className="chart-placeholder">Loading chart...</div>
          ) : categoryDistributionChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <RechartsPie data={categoryDistributionChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={120} label={{ fontSize: 12 }}>
                  {categoryDistributionChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </RechartsPie>
                <Tooltip itemStyle={{ fontSize: '12px' }} labelStyle={{ fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : !loading ? (
            <div className="chart-placeholder">No category data for selected filters.</div>
          ) : null}
        </div>
      </section>

      {habitPerformance.length > 0 && !loading && (
        <section className="habit-performance-section card">
          <h2>Habit Performance Details</h2>
          <ul className="habit-performance-list">
            {habitPerformance.map((habit) => (
              <li key={habit.id} className="habit-performance-item">
                <span className="habit-name">
                  <span className="color-dot" style={{ backgroundColor: habit.color || '#ccc' }}></span>
                  {habit.name}
                </span>
                <div className="performance-bar-container">
                  <div className="performance-bar" style={{ width: `${habit.percentage || 0}%`, backgroundColor: habit.color || '#ccc' }}></div>
                </div>
                <span className="habit-percentage">{habit.percentage || 0}%</span>
              </li>
            ))}
          </ul>
        </section>
      )}
      {loading && !habitPerformance.length && <div className="chart-placeholder card">Loading performance details...</div>}
      {!loading && !habitPerformance.length && !error && filters.selectedHabit !== 'all' && (
         <div className="chart-placeholder card">No specific performance data for this habit in the selected period.</div>
      )}
       {!loading && !habitPerformance.length && !error && filters.selectedHabit === 'all' && (
         <div className="chart-placeholder card">No performance data available for the selected period.</div>
      )}
      </div>
    </div>
  );
};

export default AnalyticsPage;
