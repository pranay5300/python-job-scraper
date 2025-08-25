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
          <a href="#resources" className="nav-link">Resources</a>
          <a href="#about" className="nav-link">About</a>
        </nav>
        
        <div className="user-section">
          <button className="btn-secondary">Sign In</button>
          <button className="btn-primary">Sign Up</button>
        </div>
      </div>
    </header>
  );
};

export default Header;
