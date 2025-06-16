import { configureStore } from '@reduxjs/toolkit';
// import counterReducer from './features/counter/counterSlice'; // Removed

export const store = configureStore({
  reducer: {
    // counter: counterReducer, // Removed
    // Add other reducers here if/when you have them
  },
});
