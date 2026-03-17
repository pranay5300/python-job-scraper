import React from 'react';
import Header from './components/Header';
import BackendStatus from './components/BackendStatus';
import EnvironmentInfo from './components/EnvironmentInfo';
import EapcetPracticeModule from './components/EapcetPracticeModule';
import './App.css';

function App() {
  return (
    <div className="App">
      <EnvironmentInfo />
      <Header />
      <main className="main-content">
        <EapcetPracticeModule />
      </main>
      <BackendStatus />
    </div>
  );
}

export default App;
