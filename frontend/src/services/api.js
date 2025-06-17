import axios from 'axios';

const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

const apiClient = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add the access token to headers
apiClient.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response error interceptor to handle 401 errors and refresh token
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refreshToken');

      if (refreshToken) {
        try {
          const refreshResponse = await axios.post(`${baseURL}/auth/refresh_token`, {}, {
            headers: { 'Authorization': `Bearer ${refreshToken}` }
          });

          if (refreshResponse.data.access_token) {
            localStorage.setItem('accessToken', refreshResponse.data.access_token);
            originalRequest.headers['Authorization'] = `Bearer ${refreshResponse.data.access_token}`;
            
            return apiClient(originalRequest);
          }
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          // For simplicity in this service file, window.location is used.
          window.location.href = '/login'; 
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token found, redirect to login
        console.log('No refresh token available.');
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }
    // For errors other than 401 or if refresh token logic fails, pass the error along
    return Promise.reject(error);
  }
);

// Habit specific API calls
export const deleteHabit = (habitId) => {
  return apiClient.delete(`/habits/${habitId}`);
};

export default apiClient;
