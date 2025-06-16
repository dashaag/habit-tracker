// AuthService for handling user authentication related functions

export const logout = () => {
  console.log('Logging out...');
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  // Redirect to login page
  // Consider using navigate from react-router-dom if used within a component context
  window.location.href = '/login'; 
};
