import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  signup: (userData) => api.post('/auth/signup', userData),
  getProfile: () => api.get('/auth/profile'),
  changePassword: (passwords) => api.post('/auth/change-password', passwords),
  forgotPassword: (email) => api.post('/auth/forgot-password', email),
  resetPassword: (data) => api.post('/auth/reset-password', data),
  deleteAccount: (password) => api.delete('/auth/delete-account', { data: { password } }),
};

// Chat API calls
export const chatAPI = {
  getChats: () => api.get('/chats'),
  createChat: (data) => api.post('/chats', data),
  getChat: (chatId) => api.get(`/chats/${chatId}`),
  updateChat: (chatId, data) => api.put(`/chats/${chatId}`, data),
  deleteChat: (chatId) => api.delete(`/chats/${chatId}`),
  sendMessage: (chatId, message) => api.post(`/chats/${chatId}/messages`, message),
  uploadFile: (chatId, formData) => api.post(`/chats/${chatId}/files`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  getChatFiles: (chatId) => api.get(`/chats/${chatId}/files`),
  deleteFile: (fileId) => api.delete(`/files/${fileId}`),
};

// Health check
export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;
