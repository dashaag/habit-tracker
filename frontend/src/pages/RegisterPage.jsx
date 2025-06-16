import React from 'react';
import RegisterForm from '../components/RegisterForm';
import './RegisterPage.scss';

const RegisterPage = () => {
  return (
    <div className="login-page"> {/* Use login-page class for consistent styling */}
      <header className="login-page__header">
        <h1 className="login-page__title">HabitFlow</h1>
        <p className="login-page__subtitle">Create your account to start building habits</p>
      </header>
      <RegisterForm />
    </div>
  );
};

export default RegisterPage;
