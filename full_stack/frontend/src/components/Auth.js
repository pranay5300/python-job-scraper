import React, { useState, useEffect } from 'react';

const Auth = ({ onAuthSuccess, onAuthFailure }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check if user is already authenticated
    const storedUser = localStorage.getItem('tamuUser');
    if (storedUser) {
      const userData = JSON.parse(storedUser);
      setUser(userData);
      onAuthSuccess(userData);
    }
    setIsLoading(false);
  }, [onAuthSuccess]);

  const handleGoogleSignIn = () => {
    setError('');
    
    // Simple email validation for demo (in production, use Google OAuth)
    const email = prompt('Please enter your TAMU email address:');
    
    if (!email) {
      return;
    }
    
    if (!email.endsWith('@tamu.edu')) {
      setError('Access restricted to @tamu.edu email addresses only.');
      onAuthFailure('Invalid email domain');
      return;
    }
    
    // Simulate successful authentication
    const userData = {
      email: email,
      name: email.split('@')[0],
      domain: 'tamu.edu',
      authenticated: true,
      timestamp: new Date().toISOString()
    };
    
    localStorage.setItem('tamuUser', JSON.stringify(userData));
    setUser(userData);
    onAuthSuccess(userData);
  };

  const handleSignOut = () => {
    localStorage.removeItem('tamuUser');
    setUser(null);
    setError('');
    onAuthFailure('User signed out');
  };

  if (isLoading) {
    return (
      <div className="auth-loading">
        <div className="loader"></div>
        <p>Checking authentication...</p>
      </div>
    );
  }

  if (user) {
    return (
      <div className="auth-success">
        <div className="user-info">
          <span className="user-icon">👤</span>
          <span className="user-email">{user.email}</span>
          <button onClick={handleSignOut} className="sign-out-btn">
            Sign Out
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>🎓 TAMU JobDataCamp Access</h2>
          <p>Exclusive access for Texas A&M University students and faculty</p>
        </div>
        
        <div className="auth-content">
          <div className="restriction-notice">
            <span className="lock-icon">🔒</span>
            <p><strong>Access Restricted:</strong> Only @tamu.edu email addresses are permitted</p>
          </div>
          
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
            </div>
          )}
          
          <button onClick={handleGoogleSignIn} className="google-signin-btn">
            <span className="google-icon">📧</span>
            Sign in with TAMU Email
          </button>
          
          <div className="auth-info">
            <h4>Why Authentication?</h4>
            <ul>
              <li>🎯 Personalized job recommendations</li>
              <li>🛂 H1B visa sponsorship predictions</li>
              <li>📊 Exclusive access to career resources</li>
              <li>🔐 Secure and private job search</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Auth;