import React, { useState } from 'react';
import Header from './components/Header';
import JobForm from './components/JobForm';
import Auth from './components/Auth';
import BackendStatus from './components/BackendStatus';
import EnvironmentInfo from './components/EnvironmentInfo';
import JobMarketAnalytics from './components/JobMarketAnalytics';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  const handleAuthSuccess = (userData) => {
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleAuthFailure = (error) => {
    setIsAuthenticated(false);
    setUser(null);
    console.log('Auth failed:', error);
  };

  if (!isAuthenticated) {
    return (
      <div className="App">
        <EnvironmentInfo />
        <Auth onAuthSuccess={handleAuthSuccess} onAuthFailure={handleAuthFailure} />
      </div>
    );
  }

  return (
    <div className="App">
      <EnvironmentInfo />
      <Auth onAuthSuccess={handleAuthSuccess} onAuthFailure={handleAuthFailure} />
      <Header />
      <main className="main-content">
        <JobForm user={user} />
        <JobMarketAnalytics showWhileLoading={true} />
      </main>
      <BackendStatus />
    </div>
  );
}

export default App;
