import React from 'react';

const Header = ({ activeModule, onModuleChange }) => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="logo-section">
          <div className="logo">
            <span className="logo-icon">JP</span>
            <span className="logo-text">JobDataCamp + TS EAPCET</span>
          </div>
        </div>
        
        <nav className="nav-section">
          <button
            type="button"
            className={`module-tab ${activeModule === 'eapcet' ? 'active-module-tab' : ''}`}
            onClick={() => onModuleChange('eapcet')}
          >
            TS EAPCET Mock Exams
          </button>
          <button
            type="button"
            className={`module-tab ${activeModule === 'jobs' ? 'active-module-tab' : ''}`}
            onClick={() => onModuleChange('jobs')}
          >
            Job Search Tools
          </button>
        </nav>
        
        <div className="user-section">
          <span className="welcome-text">Practice exams and career tools</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
