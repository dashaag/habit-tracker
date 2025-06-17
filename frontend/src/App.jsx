import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'; // Import useLocation
// import { Counter } from './features/counter/Counter'; // Removed
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage'; // Added HomePage import
import OnboardingPage from './pages/OnboardingPage'; // Added OnboardingPage import
import AnalyticsPage from './pages/AnalyticsPage'; // Added AnalyticsPage import
import Navbar from './components/Navbar'; // Import Navbar
import './App.scss';

// Define a component that includes the Navbar and uses useLocation
const AppContent = () => {
  const location = useLocation();
  const noNavPaths = ['/login', '/register']; // Paths where Navbar should be hidden

  return (
    <div className="App">
      {!noNavPaths.includes(location.pathname) && <Navbar />} {/* Conditionally render Navbar */}
      <header className="App-header">
        <Routes>
          {/* <Route path="/" element={<Counter />} /> */} {/* Removed for now, can add a Welcome page later */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} /> {/* Added OnboardingPage route */}
          <Route path="/home" element={<HomePage />} /> {/* Added HomePage route */}
          <Route path="/analytics" element={<AnalyticsPage />} /> {/* Added AnalyticsPage route */}
        </Routes>
      </header>
    </div>
  );
};

function App() {
  return (
    <Router basename="/habit-tracker/">
      <AppContent /> {/* Use the new AppContent component */}
    </Router>
  );
}

export default App;
