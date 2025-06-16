import React, { useState } from 'react';
import { deleteHabit as deleteHabitAPI } from '../services/api'; // Renamed to avoid conflict
import AddHabitLogModal from './AddHabitLogModal'; // Import the modal
import EditHabitModal from './EditHabitModal'; // Import the Edit modal
import HabitStatisticsModal from './HabitStatisticsModal'; // Import the Statistics modal
import './HabitCard.scss';

const HabitCard = ({ habit, progress, categories, onHabitLogAdded, onHabitDeleted, onHabitUpdated }) => {
  const currentProgress = progress || 0;
  const targetValue = habit.target_times && habit.target_times > 0 ? habit.target_times : 1;
  const isCompleted = currentProgress >= targetValue;
  const progressPercentage = targetValue > 0 ? Math.min((currentProgress / targetValue) * 100, 100) : 0;

  const [isMenuOpen, setIsMenuOpen] = useState(false);
  // isCompleted, currentProgress, targetValue, progressPercentage are now calculated above
  const [isAddLogModalOpen, setIsAddLogModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [habitToEditForModal, setHabitToEditForModal] = useState(null);
  const [isStatsModalOpen, setIsStatsModalOpen] = useState(false);

  const openAddLogModal = () => setIsAddLogModalOpen(true);
  const closeAddLogModal = () => setIsAddLogModalOpen(false);

  const openEditModal = () => {
    setHabitToEditForModal(habit);
    setIsEditModalOpen(true);
  };
  const closeEditModal = () => {
    setIsEditModalOpen(false);
    setHabitToEditForModal(null);
  };

  const openStatsModal = () => {
    // Clicks on child elements with their own onClick handlers that use e.stopPropagation()
    // will not trigger this card's onClick. This is the desired behavior for buttons.
    setIsStatsModalOpen(true);
  };
  const closeStatsModal = () => setIsStatsModalOpen(false);

  const toggleMenu = (e) => {
    e.stopPropagation(); // Prevent card click or other events
    setIsMenuOpen(!isMenuOpen);
  };

  const handleEdit = (e) => {
    e.stopPropagation();
    setIsMenuOpen(false);
    openEditModal();
  };

  const handleDelete = async (e) => {
    e.stopPropagation();
    setIsMenuOpen(false);

      try {
        await deleteHabitAPI(habit.id);
        console.log('Habit deleted successfully:', habit.id);
        if (onHabitDeleted) {
          onHabitDeleted(habit.id);
        }
      } catch (error) {
        console.error('Failed to delete habit:', error.response?.data?.detail || error.message);
        // Optionally, show an error message to the user
        alert(`Failed to delete habit: ${error.response?.data?.detail || error.message}`);
      }
  };

  const name = habit?.name || 'Unnamed Habit';
  // const description = habit?.description || 'No description provided.'; // Description not shown in new design
  const icon = habit?.icon || '💧'; // Default icon (e.g., water drop for 'Drink Water')

  // The small indicator icons below the habit name in the design are not implemented yet.
  // We'll need a way to represent/fetch these if they are dynamic.

  return (
    <>
      <div className={`habit-card ${isCompleted ? 'habit-card--completed' : ''}`} onClick={openStatsModal}>
        <div className="habit-card__icon-wrapper" style={{ backgroundColor: habit?.category?.color || '#E0E0E0' }}>
          {/* If habit.icon is an emoji or text, render directly. If it's a URL or identifier for an SVG/image, adjust accordingly. */}
          <span className="habit-card__icon">{icon}</span> 
        </div>
        <div className="habit-card__details">
          <div className="habit-card__name-container">
          <h3 className="habit-card__name">{name}</h3>
          <p className="habit-card__progress-text">
              {currentProgress}/{targetValue} {habit.frequency_type === 'daily' ? 'today' : habit.frequency_type ? `this ${habit.frequency_type.replace('ly', '')}` : ''}
            </p>
          </div>
          <div className="habit-card__progress-info">
            <div className="habit-card__progress-bar-container">
              <div
                className="habit-card__progress-bar"
                style={{
                  width: `${progressPercentage}%`,
                  backgroundColor: habit.category?.color || '#7EA07A', // Fallback to primary color hex
                }}
              ></div>
              <span
                className="habit-card__progress-thumb"
                style={{
                  left: `calc(${progressPercentage}% - 6px)`, // Adjust 6px based on thumb size / 2
                  color: habit.category?.color || '#7EA07A'
                }}
              >
                {icon}
              </span>
            </div>
          </div>
          {/* Placeholder for small indicator icons if needed */}
          {/* <div className="habit-card__indicators">...</div> */}
        </div>
        <div className="habit-card__actions">
          {!isCompleted ? (
            <button className="habit-card__action-button habit-card__add-log-button" onClick={openAddLogModal}>+</button>
          ) : (
            <div className="habit-card__completed-indicator">✓</div>
          )}
          <div className="habit-card__menu-container">
            <button className="habit-card__menu-button" onClick={toggleMenu} aria-label="Habit options">
              ...
            </button>
            {isMenuOpen && (
              <div className="habit-card__menu" onClick={(e) => e.stopPropagation()}>
                <button className="habit-card__menu-item" onClick={handleEdit}>Edit</button>
                <button className="habit-card__menu-item" onClick={handleDelete}>Delete</button>
              </div>
            )}
          </div>
        </div>
      </div>
      {isAddLogModalOpen && (
        <AddHabitLogModal
          habit={habit}
          isOpen={isAddLogModalOpen}  
          onClose={closeAddLogModal}
          onHabitLogAdded={onHabitLogAdded}
        />
      )}
      {isEditModalOpen && habitToEditForModal && (
        <EditHabitModal
          isOpen={isEditModalOpen}
          onClose={closeEditModal}
          habitToEdit={habitToEditForModal}
          categories={categories}
          onHabitUpdated={() => {
            if (onHabitUpdated) onHabitUpdated();
            closeEditModal();
          }}
        />
      )}
      {isStatsModalOpen && (
        <HabitStatisticsModal
          isOpen={isStatsModalOpen}
          onClose={closeStatsModal}
          habit={habit}
        />
      )}
    </>
  );
};

export default HabitCard;
