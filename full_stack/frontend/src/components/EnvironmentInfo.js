import React from 'react';

const EnvironmentInfo = () => {
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'https://python-job-scraper.onrender.com';
  const environment = process.env.REACT_APP_ENVIRONMENT || 'production';
  const isProduction = true; // Always production since we only use Render.com

  return (
    <div className="environment-info">
      <div className="env-indicator">
        <span className={`env-badge ${isProduction ? 'production' : 'development'}`}>
          {isProduction ? '🌐 PRODUCTION' : '🔧 DEVELOPMENT'}
        </span>
        <span className="backend-url">
          Backend: {isProduction ? 'Render.com' : 'Local'}
        </span>
      </div>
    </div>
  );
};

export default EnvironmentInfo;