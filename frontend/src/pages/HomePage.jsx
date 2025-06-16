import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';
import HabitCard from '../components/HabitCard';
import AddHabitModal from '../components/AddHabitModal';
import { calculateCurrentProgress } from '../utils/progressUtils';
import './HomePage.scss';

function HomePage() {
  const [groupedHabits, setGroupedHabits] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false); // For AddHabitModal
  const [categories, setCategories] = useState([]);

  const handleHabitUpdated = () => {
    fetchAndGroupHabits(false); // Refresh habits without full page loader
  };

  const handleHabitDeleted = (deletedHabitId) => {
    setGroupedHabits(prevGroupedHabits => {
      const newGroupedHabits = { ...prevGroupedHabits };
      for (const categoryName in newGroupedHabits) {
        newGroupedHabits[categoryName] = newGroupedHabits[categoryName].filter(
          habit => habit.id !== deletedHabitId
        );
        // If a category becomes empty after deletion, remove the category itself
        if (newGroupedHabits[categoryName].length === 0) {
          delete newGroupedHabits[categoryName];
        }
      }
      return newGroupedHabits;
    });
  };

  const fetchCategories = async () => {
    try {
      const response = await apiClient.get('/habits/categories');
      setCategories(response.data || []);
    } catch (err) {
      console.error('Failed to fetch categories:', err);
      // Optionally set an error state for categories as well
    }
  };

  const fetchAndGroupHabits = async (load = true) => {
    try {
      if (load) {
      setIsLoading(true);
      }
      setError(null);
      const response = await apiClient.get('/habits');
      const fetchedHabits = response.data || [];
      
      const groups = fetchedHabits.reduce((acc, habit) => {
        const categoryName = habit.category?.name || 'Uncategorized';
        if (!acc[categoryName]) {
          acc[categoryName] = [];
        }
        acc[categoryName].push(habit);
        return acc;
      }, {});
      setGroupedHabits(groups);
    } catch (err) {
      console.error('Failed to fetch habits:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to fetch habits. Please try again.');
    } finally {
       if (load) setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAndGroupHabits();
    fetchCategories();
  }, []);

  const handleAddNewHabit = () => {
    setIsModalOpen(true);
  };

  if (isLoading) {
    return (
      <div className="home-page loading-state">
        <p className="loading-message">Loading your habits...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="home-page error-state">
        <p className="error-message">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="home-page">
      <header className="home-page__header">
        <h1 className="home-page__main-title">HabitFlow</h1>
        <p className="home-page__subtitle">Track your daily habits and build consistency</p>
        <button className="home-page__add-habit-button" onClick={handleAddNewHabit}>
          <span className="icon">+</span> Add New Habit
        </button>
      </header>

      {Object.keys(groupedHabits).length > 0 ? (
        Object.entries(groupedHabits).map(([categoryName, habitsInCategory]) => (
          <section key={categoryName} className="category-section">
            <h2 className="category-section__title">{categoryName}</h2>
            <div className="habits-container">
              {habitsInCategory.map(habit => {
                const progress = calculateCurrentProgress(habit);
                return <HabitCard key={habit.id || habit.name} habit={habit} progress={progress} categories={categories} onHabitLogAdded={_ => fetchAndGroupHabits(false)} onHabitDeleted={handleHabitDeleted} onHabitUpdated={handleHabitUpdated} />;
              })}
            </div>
          </section>
        ))
      ) : (
        <div className="no-habits-state">
            <p className="no-habits-message">You haven't set up any habits yet. Get started by adding one!</p>
        </div>
      )}
      <AddHabitModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onHabitAdded={() => fetchAndGroupHabits(false)} // No loader on refresh
        categories={categories}
      />
    </div>
  );
}

export default HomePage;
