import React from 'react';

const Header = () => {
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
          <button type="button" className="module-tab active-module-tab">
            TS EAPCET Mock Exams
          </button>
        </nav>
        
        <div className="user-section">
          <span className="welcome-text">Focused practice exam mode</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
