import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { authAPI } from '../services/api';
import useAuthStore from '../store/authStore';

const SignupPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    firstName: '',
    lastName: '',
    otherName: '',
    password: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate username
    if (!formData.username.trim()) {
      toast.error('Username is required');
      return;
    }

    if (formData.username.length < 3) {
      toast.error('Username must be at least 3 characters long');
      return;
    }

    // Validate first name
    if (!formData.firstName.trim()) {
      toast.error('First name is required');
      return;
    }

    // Validate last name
    if (!formData.lastName.trim()) {
      toast.error('Last name is required');
      return;
    }

    // Validate email
    if (!formData.email.trim()) {
      toast.error('Email is required');
      return;
    }

    // Validate password
    if (formData.password.length < 8) {
      toast.error('Password must be at least 8 characters long');
      return;
    }

    // Check for uppercase letter
    if (!/[A-Z]/.test(formData.password)) {
      toast.error('Password must contain at least one uppercase letter');
      return;
    }

    // Check for lowercase letter
    if (!/[a-z]/.test(formData.password)) {
      toast.error('Password must contain at least one lowercase letter');
      return;
    }

    // Check for number
    if (!/[0-9]/.test(formData.password)) {
      toast.error('Password must contain at least one number');
      return;
    }

    // Validate password confirmation
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await authAPI.signup({
        username: formData.username,
        email: formData.email,
        first_name: formData.firstName,
        last_name: formData.lastName,
        other_name: formData.otherName || '',
        password: formData.password,
        confirm_password: formData.confirmPassword
      });

      const { user, access_token } = response.data;
      
      // Store in state
      login(user, access_token);
      
      toast.success('Account created successfully!');
      navigate('/chat');
      
    } catch (error) {
      console.error('Error signing up:', error);
      
      // Handle specific error cases
      if (error.response?.status === 409) {
        const errorMessage = error.response?.data?.error || 'Username or email already exists';
        toast.error(errorMessage);
      } else {
        const errorMessage = error.response?.data?.error || 'An error occurred. Please try again.';
        toast.error(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link
              to="/login"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              sign in to your existing account
            </Link>
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                className="input-field"
                placeholder="Enter your username"
                value={formData.username}
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>
            
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">
                First Name
              </label>
              <input
                id="firstName"
                name="firstName"
                type="text"
                autoComplete="given-name"
                required
                className="input-field"
                placeholder="Enter your first name"
                value={formData.firstName}
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>
            
            <div>
              <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">
                Last Name
              </label>
              <input
                id="lastName"
                name="lastName"
                type="text"
                autoComplete="family-name"
                required
                className="input-field"
                placeholder="Enter your last name"
                value={formData.lastName}
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>
            
            <div>
              <label htmlFor="otherName" className="block text-sm font-medium text-gray-700">
                Other Name (Optional)
              </label>
              <input
                id="otherName"
                name="otherName"
                type="text"
                autoComplete="additional-name"
                className="input-field"
                placeholder="Enter your other name (optional)"
                value={formData.otherName}
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>
            
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="input-field"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                className="input-field"
                placeholder="Create a password"
                value={formData.password}
                onChange={handleChange}
                disabled={isLoading}
              />
              <p className="mt-1 text-sm text-gray-500">
                Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number.
              </p>
            </div>
            
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                className="input-field"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Creating account...' : 'Create account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SignupPage;
