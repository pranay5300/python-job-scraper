import React from 'react';

const Header = () => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="logo-section">
          <div className="logo">
            <span className="logo-icon">💼</span>
            <span className="logo-text">JobDataCamp</span>
          </div>
        </div>
        
        <nav className="nav-section">
          <a href="#jobs" className="nav-link">Find Jobs</a>
          <a href="#companies" className="nav-link">Companies</a>
          <a href="#h1b" className="nav-link">H1B Predictions</a>
          <a href="#resources" className="nav-link">Resources</a>
        </nav>
        
        <div className="user-section">
          <span className="welcome-text">🔐 Professional Job Search</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
