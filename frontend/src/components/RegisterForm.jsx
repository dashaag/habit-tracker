import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../services/api';
import './RegisterForm.scss'; // Will create this file next
import { FaRegEnvelope, FaLock, FaEye, FaEyeSlash, FaArrowRight } from 'react-icons/fa';

const RegisterForm = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  // const [fullName, setFullName] = useState(''); // Optional: if you want to keep full name

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);

    const userData = {
      email,
      password,
      // full_name: fullName || null, // Optional: if you want to keep full name
    };

    try {
      // Assuming your register endpoint is /auth/register
      await apiClient.post('/auth/register', userData);
      // Redirect to login page on successful registration
      navigate('/login?registration=success'); // Optionally pass a query param
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="login-form"> {/* Use login-form class for styling consistency */}
      <div className="login-form__logo-container">
        <div className="login-form__logo-circle"></div>
      </div>

      <h2 className="login-form__title">Create Account</h2>
      <p className="login-form__subtitle">Join HabitFlow and start your journey</p>

      {error && <p className="error-message">{error}</p>}

      {/* Optional Full Name field - uncomment if needed
      <div className="form-group">
        <label htmlFor="fullName">Full Name</label>
        <div className="input-wrapper">
          <FaUser className="input-icon" />
          <input
            type="text"
            id="fullName"
            placeholder="Enter your full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            disabled={loading}
          />
        </div>
      </div>
      */}

      <div className="form-group">
        <label htmlFor="email">Email</label>
        <div className="input-wrapper">
          <FaRegEnvelope className="input-icon" />
          <input
            type="email"
            id="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <div className="input-wrapper">
          <FaLock className="input-icon" />
          <input
            type={showPassword ? 'text' : 'password'}
            id="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            disabled={loading}
          />
          <div className="password-toggle-icon" onClick={() => setShowPassword(!showPassword)}>
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </div>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="confirmPassword">Confirm Password</label>
        <div className="input-wrapper">
          <FaLock className="input-icon" />
          <input
            type={showConfirmPassword ? 'text' : 'password'}
            id="confirmPassword"
            placeholder="Confirm your password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            minLength={8}
            disabled={loading}
          />
          <div className="password-toggle-icon" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
            {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
          </div>
        </div>
      </div>

      <button type="submit" className="login-form__submit-btn" disabled={loading}>
        {loading ? 'Creating Account...' : 'Create Account'}
        {!loading && <FaArrowRight className="btn-icon" />}
      </button>

      <div className="login-form__register-link"> {/* Reused class for consistent styling */}
        <span>Already have an account? </span>
        <Link to="/login">Sign In</Link>
      </div>
    </form>
  );
};

export default RegisterForm;
