import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AuthError } from '../services/auth';
import Spinner from '../components/common/Spinner';
import PasswordInput from '../components/common/PasswordInput';
import './Register.css';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    passwordLength: 8
  });
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      console.log('Attempting to register user:', {
        username: formData.username,
        email: formData.email
      });

      await register(formData.username, formData.email, formData.password);
      navigate('/login', { replace: true });
    } catch (err) {
      console.error('Registration error:', err);
      const authError = err as AuthError;
      
      if (authError.code === 'ERR_BAD_REQUEST' && authError.message === 'Username already exists') {
        setError('This username is already taken. Please try a different one.');
      } else {
        setError(authError.message || 'An error occurred during registration. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="form-container">
        <h1>Create Account</h1>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              disabled={isLoading}
              placeholder="Enter your username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={isLoading}
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <PasswordInput
              value={formData.password}
              onChange={handleChange}
              required
              disabled={isLoading}
              minLength={formData.passwordLength}
            />
            <p className="password-hint">
              Password must be at least {formData.passwordLength} characters long
            </p>
          </div>

          {isLoading ? (
            <div className="spinner-container">
              <Spinner />
            </div>
          ) : (
            <button type="submit" className="btn btn-primary">
              Create Account
            </button>
          )}
        </form>
        <p className="form-footer">
          Already have an account?{' '}
          <button
            type="button"
            onClick={() => navigate('/login')}
            className="link"
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
};

export default Register; 