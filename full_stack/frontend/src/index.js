import React from 'react';
import ReactDOM from 'react-dom/client'; // Note the use of 'react-dom/client'
import App from './App'; // Make sure the path to App.js is correct

const root = ReactDOM.createRoot(document.getElementById('apple')); // Ensure 'root' matches the div ID in your public/index.html
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
