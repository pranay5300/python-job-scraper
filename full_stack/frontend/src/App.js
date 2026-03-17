import React, { useState } from 'react';
import Header from './components/Header';
import JobForm from './components/JobForm';
import BackendStatus from './components/BackendStatus';
import EnvironmentInfo from './components/EnvironmentInfo';
import JobMarketAnalytics from './components/JobMarketAnalytics';
import EapcetPracticeModule from './components/EapcetPracticeModule';
import './App.css';

function App() {
  const [activeModule, setActiveModule] = useState('eapcet');

  return (
    <div className="App">
      <EnvironmentInfo />
      <Header activeModule={activeModule} onModuleChange={setActiveModule} />
      <main className="main-content">
        {activeModule === 'jobs' ? (
          <>
            <JobForm user={null} />
            <JobMarketAnalytics />
          </>
        ) : (
          <EapcetPracticeModule />
        )}
      </main>
      <BackendStatus />
    </div>
  );
}

export default App;
