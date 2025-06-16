import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { SketchPicker } from 'react-color';
import EmojiPicker from 'emoji-picker-react';
import apiClient from '../services/api';
import './OnboardingPage.scss';

function OnboardingPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);

  // Step 1: Category state
  const [newCategoryName, setNewCategoryName] = useState('');
  const [selectedColor, setSelectedColor] = useState('#ffffff');
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [createdCategory, setCreatedCategory] = useState(null);

  // Step 2: Habit state
  const [newHabitName, setNewHabitName] = useState('');
  const [selectedHabitEmoji, setSelectedHabitEmoji] = useState('🏃');
  const [showHabitEmojiPicker, setShowHabitEmojiPicker] = useState(false);
  const [frequencyType, setFrequencyType] = useState('daily'); // Default to daily
  const [targetTimes, setTargetTimes] = useState(1); // Default to 1
  const [selectedTimes, setSelectedTimes] = useState([]); // For daily frequency, specific times
  const [selectedDays, setSelectedDays] = useState([]); // For weekly frequency, array of day numbers (0-6)

  useEffect(() => {
    if (frequencyType === 'daily') {
      const currentTarget = parseInt(targetTimes, 10);
      if (currentTarget > 0 && selectedTimes.length !== currentTarget) {
        // Adjust selectedTimes array to match targetTimes, preserving existing values
        const newSelectedTimes = Array(currentTarget).fill('');
        for (let i = 0; i < Math.min(selectedTimes.length, currentTarget); i++) {
          newSelectedTimes[i] = selectedTimes[i];
        }
        setSelectedTimes(newSelectedTimes);
      }
    } else {
      // Clear selected times if not daily
      setSelectedTimes([]);
    }

    // Clear selected days if not weekly
    if (frequencyType !== 'weekly') {
      setSelectedDays([]);
    }
    // Reset targetTimes to 1 if switching away from daily to weekly, to avoid NaN issues if it was empty
    if (frequencyType === 'weekly') {
        setTargetTimes(1); // Or any default/appropriate value for weekly if it were to be used
    }

  }, [targetTimes, frequencyType, selectedTimes]);

  // General state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const onHabitEmojiClick = (emojiObject) => {
    setSelectedHabitEmoji(emojiObject.emoji);
    setShowHabitEmojiPicker(false);
  };

  const handleAddCategory = async (e) => {
    e.preventDefault();
    if (!newCategoryName.trim()) {
      setError('Please provide a name for the category.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const response = await apiClient.post('/habits/categories', {
        name: newCategoryName,
        color: selectedColor, // Send color hex code as the color
      });
      setCreatedCategory(response.data);
      setStep(2); // Move to the next step
    } catch (err) {
      console.error('Failed to add category:', err);
      setError(err.response?.data?.detail || 'Failed to add category.');
    }
    setIsLoading(false);
  };

  const handleTimeChange = (index, value) => {
    const newTimes = [...selectedTimes];
    // Ensure the array is long enough, fill with empty strings if needed
    while (newTimes.length <= index) {
      newTimes.push('');
    }
    newTimes[index] = value;
    setSelectedTimes(newTimes);
  };

  const handleDayChange = (dayValue) => {
    setSelectedDays(prevSelectedDays => 
      prevSelectedDays.includes(dayValue) 
        ? prevSelectedDays.filter(d => d !== dayValue) 
        : [...prevSelectedDays, dayValue]
    );
  };

  const handleAddHabit = async (e) => {
    e.preventDefault();
    if (!newHabitName.trim() || !selectedHabitEmoji) {
      setError('Please provide a name and icon for the habit.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const habitPayload = {
        name: newHabitName,
        icon: selectedHabitEmoji,
        category_id: createdCategory.id,
        frequency_type: frequencyType,
        // target_times will be set based on frequency type
        reminder_on: false, // Assuming default, can be changed later
      };

      if (frequencyType === 'daily') {
        habitPayload.target_times = parseInt(targetTimes, 10) || 0;
        habitPayload.times_of_day = JSON.stringify(selectedTimes.slice(0, parseInt(targetTimes, 10)).filter(t => t));
        habitPayload.days_of_week = JSON.stringify([]);
      } else if (frequencyType === 'weekly') {
        // Placeholder for weekly specific logic - for now, send empty arrays
        habitPayload.times_of_day = JSON.stringify([]);
        habitPayload.days_of_week = JSON.stringify(selectedDays.map(String)); // Ensure days are strings 
        habitPayload.target_times = selectedDays.length; // For weekly, target_times is the number of selected days
      }

      await apiClient.post('/habits', habitPayload);
      navigate('/home'); // On success, navigate to the dashboard
    } catch (err) {
      console.error('Failed to add habit:', err);
      setError(err.response?.data?.detail || 'Failed to add habit.');
      setIsLoading(false);
    }
  };

  const handleFinishOnboarding = () => {
    navigate('/home');
  };

  return (
    <div className="onboarding-page">
      <header className="onboarding-page__header">
        <h1 className="onboarding-page__title">HabitFlow</h1>
        <p className="onboarding-page__subtitle">Let's get you started! Set up your first habit.</p>
      </header>
      <div className="onboarding-card">
        {step === 1 ? (
          <>
            <h2 className="onboarding-card__step-title">Step 1: Create a Category</h2>
            <p className="onboarding-card__step-description">Let's start by creating a category for your new habit.</p>
          </>
        ) : (
          <>
            <h2 className="onboarding-card__step-title">Step 2: Add a Habit</h2>
            <p className="onboarding-card__step-description">Great! Now add your first habit to the "{createdCategory?.name}" category.</p>
          </>
        )}

        {error && <p className="error-message">{error}</p>}

        {step === 1 ? (
          <div className="onboarding-card__current-step-content">
            <form onSubmit={handleAddCategory} className="category-form">
              <div className="form-group category-name-group">
                <div className="color-picker-container">
                  <div
                    className="color-swatch"
                    style={{ backgroundColor: selectedColor }}
                    onClick={() => setShowColorPicker(!showColorPicker)}
                  />
                  {showColorPicker && (
                    <div className="color-picker-popover">
                      <div className="color-picker-cover" onClick={() => setShowColorPicker(false)} />
                      <SketchPicker color={selectedColor} onChange={(color) => setSelectedColor(color.hex)} />
                    </div>
                  )}
                </div>
                <input
                  type="text"
                  id="categoryName"
                  value={newCategoryName}
                  onChange={(e) => setNewCategoryName(e.target.value)}
                  placeholder="E.g., Fitness"
                  required
                  disabled={isLoading}
                />
              </div>
              <button type="submit" disabled={isLoading} className="onboarding-card__button">
                {isLoading ? 'Creating...' : 'Create Category & Next'}
              </button>
            </form>
          </div>
        ) : (
          <div className="onboarding-card__current-step-content">
            <form onSubmit={handleAddHabit} className="habit-form">
              <div className="form-group category-name-group">
                <div className="emoji-picker-container">
                  <button type="button" className="emoji-button" onClick={() => setShowHabitEmojiPicker(!showHabitEmojiPicker)}>
                    {selectedHabitEmoji}
                  </button>
                  {showHabitEmojiPicker && (
                    <div className="emoji-picker-wrapper">
                      <EmojiPicker onEmojiClick={onHabitEmojiClick} />
                    </div>
                  )}
                </div>
                <input
                  type="text"
                  id="habitName"
                  value={newHabitName}
                  onChange={(e) => setNewHabitName(e.target.value)}
                  placeholder="E.g., Go for a 30-min run"
                  required
                  disabled={isLoading}
                />
              </div>
              <div className="form-group frequency-group">
                <label htmlFor="frequencyType">Frequency:</label>
                <select 
                  id="frequencyType" 
                  value={frequencyType} 
                  onChange={(e) => setFrequencyType(e.target.value)}
                  disabled={isLoading}
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>

              {frequencyType === 'daily' && (
                <div className="form-group target-times-group">
                  <label htmlFor="targetTimes">Times Per Day:</label>
                  <input 
                    type="number" 
                    id="targetTimes" 
                    value={targetTimes} 
                    onChange={(e) => setTargetTimes(Math.max(1, parseInt(e.target.value, 10) || 1))} 
                    min="1" 
                    max="30" 
                    disabled={isLoading}
                    required 
                  />
                </div>
              )}

              {frequencyType === 'daily' && (
                <div className="time-pickers-group">
                  <label>Specific Times:</label>
                  {Array.from({ length: parseInt(targetTimes, 10) || 0 }).map((_, index) => (
                    <div key={index} className="form-group time-picker-item">
                      <input 
                        type="time" 
                        value={selectedTimes[index] || ''} 
                        onChange={(e) => handleTimeChange(index, e.target.value)} 
                        disabled={isLoading}
                      />
                    </div>
                  ))}
                </div>
              )}

              {frequencyType === 'weekly' && (
                <div className="days-selector-group">
                  <label>Select Days:</label>
                  <div className="days-checkboxes">
                    {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((dayName, index) => (
                      <label key={index} className="day-checkbox-label">
                        <input 
                          type="checkbox" 
                          value={index} 
                          checked={selectedDays.includes(index)} 
                          onChange={() => handleDayChange(index)} 
                          disabled={isLoading} 
                        />
                        {dayName}
                      </label>
                    ))}
                  </div>
                </div>
              )}
              
              <button type="submit" disabled={isLoading} className="onboarding-card__button">
                {isLoading ? 'Adding...' : 'Add Habit and Finish'}
              </button>
            </form>
          </div>
        )}
        <div className="onboarding-card__skip-link">
          <button onClick={handleFinishOnboarding} className="button-as-link">
            Skip for Now & Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}

export default OnboardingPage;
