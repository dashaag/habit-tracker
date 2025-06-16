import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { logout } from '../services/authService';
import './Navbar.scss'; // We'll create this for basic styling

const Navbar = () => {
  const location = useLocation();
  const handleLogout = () => {
    logout();
    // The logout service already handles redirection, but if it were to change,
    // navigate('/login'); // could be used here.
  };

  // Check if a token exists to determine if the user is logged in
  // This is a simple check; a more robust solution might use an auth context
  const isLoggedIn = !!localStorage.getItem('accessToken');

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="navbar-item">HabitTracker</Link>
      </div>
      <div className="navbar-menu">
        <div className="navbar-end">
          {isLoggedIn ? (
            <>
              {/* Logout button always visible when logged in */}
              <button onClick={handleLogout} className="navbar-item button is-light">
                Logout
              </button>
              {/* Additional links for authenticated users, not shown on onboarding */}
              {location.pathname !== '/onboarding' && (
                <> 
                  <Link to="/analytics" className="navbar-item">Analytics</Link>
                  {/* Example: <Link to="/dashboard" className="navbar-item">Dashboard</Link> */}
                  {/* Add other authenticated links here as needed */}
                </>
              )}
            </>
          ) : (
            <>
              <Link to="/login" className="navbar-item button is-light">
                Login
              </Link>
              <Link to="/register" className="navbar-item button is-primary">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
