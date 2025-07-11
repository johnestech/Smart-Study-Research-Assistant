# SignupPage Test Documentation

## Overview
This test file verifies the SignupPage component functionality, specifically testing the backend contract compliance and error handling.

## Test Cases

### 1. Successful Signup (201 Status)
- Tests that the signup form sends the correct payload to the backend
- Verifies that on successful signup (201 response), the user is logged in and redirected to chat
- Ensures the authStore.login() is called with user data and access_token

### 2. Duplicate Username/Email Error (409 Status)
- Tests error handling for duplicate username/email scenarios
- Verifies that the 409 error is properly handled and displayed to the user
- Ensures no login occurs and no navigation happens on error

## Running the Tests

To run these tests:

```bash
npm test -- --testPathPattern=SignupPage.test.js
```

## Test Coverage

The tests cover:
- ✅ Form validation for all new fields (username, first_name, last_name, other_name)
- ✅ Backend API payload structure compliance
- ✅ 201 success response handling
- ✅ 409 error response handling
- ✅ Zustand store integration
- ✅ Navigation on success
- ✅ Client-side validation reuse for password fields

## Backend Contract Validation

The test verifies that the signup payload matches the backend contract:
```javascript
{
  username,
  email,
  first_name,
  last_name,
  other_name,
  password,
  confirm_password
}
```

This ensures that the frontend properly communicates with the backend and handles both success and error scenarios correctly.
