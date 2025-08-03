/**
 * Application Entry Point
 * Initializes and renders the React application with proper error handling
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

// Get root element
const container = document.getElementById('root');

if (!container) {
  throw new Error('Root element not found. Make sure you have a <div id="root"></div> in your HTML.');
}

// Create React root
const root = createRoot(container);

// Development mode setup
if (import.meta.env.DEV) {
  // Enable React DevTools in development
  if (typeof window !== 'undefined') {
    window.__REACT_DEVTOOLS_GLOBAL_HOOK__?.onCommitFiberRoot = 
      window.__REACT_DEVTOOLS_GLOBAL_HOOK__?.onCommitFiberRoot || (() => {});
  }
}

// Render application
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Development HMR (Hot Module Replacement) setup
if (import.meta.env.DEV && import.meta.hot) {
  import.meta.hot.accept();
}

// Production performance monitoring
if (import.meta.env.PROD) {
  // Register service worker for PWA capabilities (future implementation)
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      // Service worker registration would go here
      console.log('Service worker support detected');
    });
  }

  // Global error handling for production
  window.addEventListener('error', (event) => {
    console.error('Global error caught:', event.error);
    // In a real app, you would send this to a logging service
  });

  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    // In a real app, you would send this to a logging service
  });
}