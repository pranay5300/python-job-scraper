import React from 'react';
import Header from './components/Header';
import JobForm from './components/JobForm';
import './App.css';

function App() {
  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <JobForm />
      </main>
    </div>
  );
}

export default App;
