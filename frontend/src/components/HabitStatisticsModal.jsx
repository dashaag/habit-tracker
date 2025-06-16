import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import dayjs from 'dayjs';
import './HabitStatisticsModal.scss';
import api from '../services/api'; // Assuming you have an api service

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const HabitStatisticsModal = ({ isOpen, onClose, habit }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalCompletions: 0,
    avgCompletion: 0,
  });
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Completions',
        data: [],
        borderColor: 'rgb(160, 210, 160)',
        backgroundColor: 'rgba(160, 210, 160, 0.1)',
        tension: 0.1,
        pointRadius: 5,
        pointBackgroundColor: 'rgb(160, 210, 160)',
        fill: true,
      },
    ],
  });

  useEffect(() => {
    if (isOpen && habit && habit.id) {
      const fetchStatistics = async () => {
        setLoading(true);
        setError(null);
        try {
          // Assuming your api service is configured for base URL and auth
          const response = await api.get(`/habits/${habit.id}/statistics`); // Using full path for clarity
          const data = response.data; // API returns { total_completions: number, daily_stats: [{date: string, value: number}] }

          const labels = data.daily_stats.map(stat => dayjs(stat.date).format('MMM DD'));
          const completionData = data.daily_stats.map(stat => stat.value);

          setChartData(prevChartData => ({
            ...prevChartData,
            labels,
            datasets: [
              {
                ...prevChartData.datasets[0],
                data: completionData,
              },
            ],
          }));

          let avgCompletion = 0;
          if (data.daily_stats.length > 0) {
            const totalPossible = (habit.target_times || 1) * data.daily_stats.length;
            avgCompletion = totalPossible > 0 ? (data.total_completions / totalPossible) * 100 : 0;
          }

          setStats({
            totalCompletions: data.total_completions,
            avgCompletion: Math.round(avgCompletion),
          });

        } catch (err) {
          console.error('Failed to fetch habit statistics:', err);
          setError('Failed to load statistics. Please try again later.');
        } finally {
          setLoading(false);
        }
      };

      fetchStatistics();
    } else {
      // Reset when modal is closed or habit is not available
      setChartData({
        labels: [],
        datasets: [
          {
            label: 'Completions',
            data: [],
            borderColor: 'rgb(160, 210, 160)',
            backgroundColor: 'rgba(160, 210, 160, 0.1)',
            tension: 0.1,
            pointRadius: 5,
            pointBackgroundColor: 'rgb(160, 210, 160)',
            fill: true,
          },
        ],
      });
      setStats({ totalCompletions: 0, avgCompletion: 0 });
      setError(null);
      setLoading(false);
    }
  }, [isOpen, habit]);

  if (!isOpen || !habit) {
    return null;
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        // Suggested max based on image, can be dynamic
        suggestedMax: Math.max(2.5, habit.target_times || 2.5, ...chartData.datasets[0]?.data || [2.5]) + 0.5,
        grid: {
          color: 'rgba(200, 200, 200, 0.2)', // Lighter grid lines
        }
      },
      x: {
        grid: {
          display: false, // No vertical grid lines
        }
      }
    },
    plugins: {
      legend: {
        display: false, // Legend not shown in image
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        titleFont: { size: 14 },
        bodyFont: { size: 12 },
        padding: 10,
        cornerRadius: 4,
      }
    },
  };

  return (
    <div className="habit-statistics-modal-overlay">
      <div className="habit-statistics-modal-content">
        <div className="modal-header">
          <h2>{habit.name} Statistics</h2>
          <button onClick={onClose} className="close-button">
            &times;
          </button>
        </div>
        <div className="modal-body">
          <div className="stats-summary">
            <div className="stat-card">
              <span className="stat-value">{stats.totalCompletions}</span>
              <span className="stat-label">Total Completions</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{habit.target_times || 1}</span>
              <span className="stat-label">Daily Target</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{stats.avgCompletion}%</span>
              <span className="stat-label">Avg. Completion</span>
            </div>
          </div>
          <div className="chart-container">
            {loading && <p className="loading-message">Loading statistics...</p>}
            {error && <p className="error-message">{error}</p>}
            {!loading && !error && chartData.labels && chartData.labels.length > 0 && (
              <Line options={chartOptions} data={chartData} />
            )}
            {!loading && !error && (!chartData.labels || chartData.labels.length === 0) && (
              <p className="no-data-message">No statistics available for the selected period.</p>
            )}
          </div>
          <p className="chart-footer-text">Last 30 days completion history</p>
        </div>
      </div>
    </div>
  );
};

HabitStatisticsModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  habit: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    name: PropTypes.string.isRequired,
    target_times: PropTypes.number,
    // Add other habit properties if needed
  }),
};

export default HabitStatisticsModal;
