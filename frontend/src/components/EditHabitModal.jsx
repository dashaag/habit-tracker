import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';
import './EditHabitModal.scss';

const ICONS = ['💧', '💪', '📖', '🧘', '🍎', '💻', '☀️', '🌙'];
const COLORS = ['#7ea07a', '#ffab91', '#81d4fa', '#ce93d8', '#fff59d', '#a5d6a7', '#bcaaa4', '#eeeeee'];

const EditHabitModal = ({ isOpen, onClose, onHabitUpdated, categories, habitToEdit }) => {
  const [habitName, setHabitName] = useState('');
  const [selectedCategoryId, setSelectedCategoryId] = useState('');
  const [newCategoryName, setNewCategoryName] = useState('');
  const [isCreatingNewCategory, setIsCreatingNewCategory] = useState(false);
  const [selectedIcon, setSelectedIcon] = useState(ICONS[0]);
  const [selectedColor, setSelectedColor] = useState(COLORS[0]);
  const [frequencyType, setFrequencyType] = useState('daily');
  const [targetTimes, setTargetTimes] = useState(1);
  const [selectedDays, setSelectedDays] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTimes, setSelectedTimes] = useState([]); // For daily frequency, specific times

  useEffect(() => {
    if (isOpen && habitToEdit) {
      setHabitName(habitToEdit.name || '');
      setSelectedCategoryId(habitToEdit.category_id || (categories.length > 0 ? categories[0].id : ''));
      setNewCategoryName('');
      setIsCreatingNewCategory(false);
      setSelectedIcon(habitToEdit.icon || ICONS[0]);
      // Color is for new category creation, not directly for habit editing here
      setSelectedColor(COLORS[0]); 
      setFrequencyType(habitToEdit.frequency_type || 'daily');
      setTargetTimes(habitToEdit.target_times || 1);
      
      // Parse days_of_week (e.g., "0,2,4") into array of numbers
      const daysArray = habitToEdit.days_of_week ? habitToEdit.days_of_week.split(',').map(Number) : [];
      setSelectedDays(daysArray);
      
      // Parse times_of_day (e.g., "08:00,12:30") into array of strings
      const timesArray = habitToEdit.times_of_day ? habitToEdit.times_of_day.split(',') : [];
      setSelectedTimes(timesArray);
      
      setError(null);
    } else if (isOpen) {
      // Reset form if opening for a new habit (though this modal is for editing)
      // Or if habitToEdit is not yet available, provide sensible defaults
      setHabitName('');
      setSelectedCategoryId(categories.length > 0 ? categories[0].id : '');
      setNewCategoryName('');
      setIsCreatingNewCategory(false);
      setSelectedIcon(ICONS[0]);
      setSelectedColor(COLORS[0]);
      setFrequencyType('daily');
      setTargetTimes(1);
      setSelectedDays([]);
      setSelectedTimes([]);
      setError(null);
    }
  }, [isOpen, habitToEdit, categories]);

  useEffect(() => {
    if (frequencyType !== 'weekly') {
      setSelectedDays([]);
    }
    // Manage selectedTimes based on targetTimes for daily frequency
    if (frequencyType === 'daily') {
      const currentTarget = parseInt(targetTimes, 10);
      if (currentTarget > 0 && selectedTimes.length !== currentTarget) {
        const newSelectedTimes = Array(currentTarget).fill('');
        for (let i = 0; i < Math.min(selectedTimes.length, currentTarget); i++) {
          newSelectedTimes[i] = selectedTimes[i];
        }
        setSelectedTimes(newSelectedTimes);
      }
    } else {
      setSelectedTimes([]); // Clear selected times if not daily
      setTargetTimes(1); // Reset targetTimes if not daily, or if frequencyType changes away from daily
    }
  }, [frequencyType, targetTimes, selectedTimes]); // Ensure targetTimes and selectedTimes are dependencies

  if (!isOpen) {
    return null;
  }

  const handleDayChange = (dayValue) => {
    setSelectedDays(prevSelectedDays => 
      prevSelectedDays.includes(dayValue) 
        ? prevSelectedDays.filter(d => d !== dayValue) 
        : [...prevSelectedDays, dayValue]
    );
  };

  const handleTimeChange = (index, value) => {
    const newTimes = [...selectedTimes];
    // Ensure the array is long enough
    while (newTimes.length <= index) {
      newTimes.push('');
    }
    newTimes[index] = value;
    setSelectedTimes(newTimes);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      let categoryId = selectedCategoryId;

      if (isCreatingNewCategory) {
        if (!newCategoryName.trim()) {
          setError('New category name cannot be empty.');
          setIsSubmitting(false);
          return;
        }
        // Create the new category first
        const categoryPayload = { name: newCategoryName, color: selectedColor };
        const categoryResponse = await apiClient.post('/habits/categories', categoryPayload);
        categoryId = categoryResponse.data.id;
      }

      if (!habitName.trim()) {
        setError('Habit name cannot be empty.');
        setIsSubmitting(false);
        return;
      }

      // Create the new habit
      const habitPayload = {
        name: habitName,
        category_id: categoryId ? parseInt(categoryId, 10) : null,
        icon: selectedIcon,
        frequency_type: frequencyType,
        target_times: frequencyType === 'daily' ? parseInt(targetTimes, 10) : null,
        days_of_week: frequencyType === 'weekly' && selectedDays.length > 0 ? selectedDays.map(String).join(',') : null,
        times_of_day: frequencyType === 'daily' && selectedTimes.filter(t => t).length > 0 ? selectedTimes.filter(t => t).join(',') : null,
        // reminder_on and streak_goal can be added here if UI elements are implemented
      };

      await apiClient.put(`/habits/${habitToEdit.id}`, habitPayload);

      await onHabitUpdated();
      onClose();
    } catch (err) {
      console.error('Failed to update habit:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to update habit.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content add-habit-modal">
        <button className="modal-close-button" onClick={onClose} aria-label="Close modal">✕</button>
        <h3>Edit Habit</h3>
        <form onSubmit={handleSubmit} className="add-habit-form">
          <div className="form-group">
            <label htmlFor="categorySelect">Category</label>
            {!isCreatingNewCategory ? (
              <select
                id="categorySelect"
                value={selectedCategoryId}
                onChange={(e) => setSelectedCategoryId(e.target.value)}
                disabled={isCreatingNewCategory}
              >
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            ) : (
              <>
                <input
                  type="text"
                  id="newCategoryName"
                  value={newCategoryName}
                  onChange={(e) => setNewCategoryName(e.target.value)}
                  placeholder="Enter new category name"
                  required
                  style={{ marginBottom: '1rem' }} 
                />
                <label style={{ marginBottom: '0.5rem', display: 'block', fontWeight: '600', color: '#333' }}>Category Color</label>
                <div className="color-selector" style={{ marginBottom: '1rem' }}>
                  {COLORS.map(color => (
                    <button
                      key={color}
                      type="button"
                      className={`color-option ${selectedColor === color ? 'selected' : ''}`}
                      style={{ backgroundColor: color }}
                      onClick={() => setSelectedColor(color)}
                    />
                  ))}
                </div>
              </>
            )}
            <button type="button" className="toggle-category-button" onClick={() => setIsCreatingNewCategory(!isCreatingNewCategory)}>
              {isCreatingNewCategory ? 'Select Existing' : 'Create New'}
            </button>
          </div>
          <div className="form-group">
            <label htmlFor="habitName">Habit Name</label>
            <input
              type="text"
              id="habitName"
              value={habitName}
              onChange={(e) => setHabitName(e.target.value)}
              placeholder="e.g., Drink Water"
              required
            />
          </div>

          <div className="form-group">
            <label>Icon</label>
            <div className="icon-selector">
              {ICONS.map(icon => (
                <button
                  key={icon}
                  type="button"
                  className={`icon-option ${selectedIcon === icon ? 'selected' : ''}`}
                  onClick={() => setSelectedIcon(icon)}
                >
                  {icon}
                </button>
              ))}
            </div>
          </div>


          <div className="form-group frequency-group">
            <label htmlFor="frequencyType">Frequency</label>
            <select 
              id="frequencyType" 
              value={frequencyType} 
              onChange={(e) => setFrequencyType(e.target.value)}
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>

          {frequencyType === 'daily' && (
            <>
              <div className="form-group target-times-group">
                <label htmlFor="targetTimes">Times Per Day</label>
                <input 
                  type="number" 
                  id="targetTimes" 
                  value={targetTimes} 
                  onChange={(e) => setTargetTimes(Math.max(1, parseInt(e.target.value, 10) || 1))} 
                  min="1" 
                  max="30" 
                  disabled={isSubmitting}
                  required 
                />
              </div>
              <div className="time-pickers-group">
                <label>Specific Times (Optional)</label>
                {Array.from({ length: parseInt(targetTimes, 10) || 0 }).map((_, index) => (
                  <div key={index} className="form-group time-picker-item">
                    <input 
                      type="time" 
                      value={selectedTimes[index] || ''} 
                      onChange={(e) => handleTimeChange(index, e.target.value)} 
                      disabled={isSubmitting}
                    />
                  </div>
                ))}
              </div>
            </>
          )}

          {frequencyType === 'weekly' && (
            <div className="form-group days-selector-group">
              <label>Select Days</label>
              <div className="days-checkboxes">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((dayName, index) => (
                  <label key={index} className="day-checkbox-label">
                    <input 
                      type="checkbox" 
                      value={index} 
                      checked={selectedDays.includes(index)} 
                      onChange={() => handleDayChange(index)} 
                    />
                    <span>{dayName}</span>
                  </label>
                ))}
              </div>
            </div>
          )}



          {error && <p className="error-message">{error}</p>}

          <div className="modal-actions">
            <button type="button" className="button button--cancel" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </button>
            <button type="submit" className="button button--primary" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditHabitModal;
