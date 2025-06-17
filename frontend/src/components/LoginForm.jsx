import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../services/api';
import './LoginForm.scss';
import { FaRegEnvelope, FaLock, FaEye, FaEyeSlash, FaArrowRight } from 'react-icons/fa';

const LoginForm = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
      const response = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      localStorage.setItem('accessToken', response.data.access_token);
      localStorage.setItem('refreshToken', response.data.refresh_token);
      navigate(`${process.env.PUBLIC_URL}/onboarding`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <div className="login-form__logo-container">
        <div className="login-form__logo-circle"></div>
      </div>

      <h2 className="login-form__title">Welcome Back</h2>
      <p className="login-form__subtitle">Sign in to continue your habit journey</p>

      {error && <p className="error-message">{error}</p>}

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
            disabled={loading}
          />
          <div className="password-toggle-icon" onClick={() => setShowPassword(!showPassword)}>
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </div>
        </div>
      </div>

      <button type="submit" className="login-form__submit-btn" disabled={loading}>
        {loading ? 'Signing In...' : 'Sign In'}
        {!loading && <FaArrowRight className="btn-icon" />}
      </button>

      <div className="login-form__register-link">
        <span>Don't have an account? </span>
        <Link to="/register">Register</Link>
      </div>
    </form>
  );
};

export default LoginForm;
