import React, { useState } from 'react';
import Header from './components/Header';
import JobForm from './components/JobForm';
import Auth from './components/Auth';
import BackendStatus from './components/BackendStatus';
import EnvironmentInfo from './components/EnvironmentInfo';
import JobMarketAnalytics from './components/JobMarketAnalytics';
import EapcetPracticeModule from './components/EapcetPracticeModule';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [activeModule, setActiveModule] = useState('eapcet');

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
      <Header activeModule={activeModule} onModuleChange={setActiveModule} />
      <main className="main-content">
        {activeModule === 'jobs' ? (
          <>
            <JobForm user={user} />
            <JobMarketAnalytics />
          </>
        ) : (
          <EapcetPracticeModule user={user} />
        )}
      </main>
      <BackendStatus />
    </div>
  );
}

export default App;
