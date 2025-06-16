import React from 'react';
import LoginForm from '../components/LoginForm';
import './LoginPage.scss';

const LoginPage = () => {
  return (
    <div className="login-page">
      <header className="login-page__header">
        <h1 className="login-page__title">HabitFlow</h1>
        <p className="login-page__subtitle">Build better habits, one day at a time</p>
      </header>
      <LoginForm />
    </div>
  );
};

export default LoginPage;
