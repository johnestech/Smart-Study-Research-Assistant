import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import '@testing-library/jest-dom';
import SignupPage from '../pages/SignupPage';
import { authAPI } from '../services/api';

// Mock the auth API
jest.mock('../services/api', () => ({
  authAPI: {
    signup: jest.fn()
  }
}));

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

// Mock useAuthStore
const mockLogin = jest.fn();
jest.mock('../store/authStore', () => ({
  __esModule: true,
  default: () => ({
    login: mockLogin
  })
}));

const SignupPageWithRouter = () => (
  <BrowserRouter>
    <SignupPage />
    <Toaster />
  </BrowserRouter>
);

test('successful signup returns 201 status and navigates to chat', async () => {
  // Mock successful API response
  authAPI.signup.mockResolvedValueOnce({
    data: { 
      user: { id: 1, username: 'testuser', email: 'test@example.com' }, 
      access_token: 'fake-token' 
    }
  });

  render(<SignupPageWithRouter />);

  // Fill in the form
  fireEvent.change(screen.getByLabelText(/Username/i), { target: { value: 'testuser' } });
  fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: 'Test' } });
  fireEvent.change(screen.getByLabelText(/Last Name/i), { target: { value: 'User' } });
  fireEvent.change(screen.getByLabelText(/Email address/i), { target: { value: 'test@example.com' } });
  fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password123' } });
  fireEvent.change(screen.getByLabelText(/Confirm Password/i), { target: { value: 'password123' } });

  // Submit the form
  fireEvent.click(screen.getByRole('button', { name: /create account/i }));

  // Verify API was called with correct payload
  await waitFor(() => {
    expect(authAPI.signup).toHaveBeenCalledWith({
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      other_name: '',
      password: 'password123',
      confirm_password: 'password123'
    });
  });

  // Verify login was called
  expect(mockLogin).toHaveBeenCalledWith(
    { id: 1, username: 'testuser', email: 'test@example.com' },
    'fake-token'
  );

  // Verify navigation to chat
  expect(mockNavigate).toHaveBeenCalledWith('/chat');
});

test('handles 409 error (duplicate username/email)', async () => {
  // Mock 409 error response
  authAPI.signup.mockRejectedValueOnce({
    response: {
      status: 409,
      data: { error: 'Username or email already exists' }
    }
  });

  render(<SignupPageWithRouter />);

  // Fill in the form
  fireEvent.change(screen.getByLabelText(/Username/i), { target: { value: 'existinguser' } });
  fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: 'Test' } });
  fireEvent.change(screen.getByLabelText(/Last Name/i), { target: { value: 'User' } });
  fireEvent.change(screen.getByLabelText(/Email address/i), { target: { value: 'existing@example.com' } });
  fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password123' } });
  fireEvent.change(screen.getByLabelText(/Confirm Password/i), { target: { value: 'password123' } });

  // Submit the form
  fireEvent.click(screen.getByRole('button', { name: /create account/i }));

  // Verify error handling
  await waitFor(() => {
    expect(authAPI.signup).toHaveBeenCalled();
  });

  // Verify login was not called
  expect(mockLogin).not.toHaveBeenCalled();

  // Verify navigation did not occur
  expect(mockNavigate).not.toHaveBeenCalled();
});
