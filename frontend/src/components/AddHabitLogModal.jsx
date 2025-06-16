import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';
import './AddHabitLogModal.scss';

const AddHabitLogModal = ({ habit, isOpen, onClose, onHabitLogAdded }) => {
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && habit) {
      const now = new Date();
      // Format for date input: YYYY-MM-DD
      const year = now.getFullYear();
      const month = (now.getMonth() + 1).toString().padStart(2, '0');
      const day = now.getDate().toString().padStart(2, '0');
      setSelectedDate(`${year}-${month}-${day}`);

      // Format for time input: HH:MM
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      setSelectedTime(`${hours}:${minutes}`);
      
      setError(null); // Clear previous errors
    }
  }, [isOpen, habit]);

  if (!isOpen) {
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      // Ensure habit and habit.id are available
      if (!selectedDate || !selectedTime) {
        setError("Date and Time are required.");
        setIsSubmitting(false); // Ensure isSubmitting is reset
        return;
      }
      if (!habit || typeof habit.id === 'undefined') {
        setError('Habit information is missing. Cannot log.');
        setIsSubmitting(false); // Ensure isSubmitting is reset
        return;
      }
      await apiClient.post('/tracking-log/', { // Assuming POST /tracking-log/ is the endpoint
        habit_id: habit.id,
        logged_at: new Date(`${selectedDate}T${selectedTime}:00`).toISOString(),
      });
      if (onHabitLogAdded) {
        await onHabitLogAdded(); // Await for the habit list to refresh
      }
      onClose(); // Close modal after successful refresh
    } catch (err) {
      console.error('Failed to add habit log:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to save log. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close-button" onClick={onClose} aria-label="Close modal">✕</button>
        <h3>Add Completion for {habit?.name || 'Habit'}</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="logDate">Date</label>
            <div className="input-with-icon">
              <span className="input-icon">📅</span>
              <input
                type="date"
                id="logDate"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                required
              />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="logTime">Time</label>
            <div className="input-with-icon">
              <span className="input-icon">🕒</span>
              <input
                type="time"
                id="logTime"
                value={selectedTime}
                onChange={(e) => setSelectedTime(e.target.value)}
                required
              />
            </div>
          </div>
          {error && <p className="error-message">{error}</p>}
          <div className="modal-actions">
            <button type="button" className="button button--cancel" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </button>
            <button type="submit" className="button button--primary" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Add Completion'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddHabitLogModal;
