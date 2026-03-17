import React, { useState, useEffect } from 'react';

const Auth = ({ onAuthSuccess, onAuthFailure }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [password, setPassword] = useState('');
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [changePasswordData, setChangePasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  // Backend URL configuration - Always use Render.com
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://python-job-scraper.onrender.com';

  useEffect(() => {
    // Check if user is already authenticated
    const storedUser = localStorage.getItem('jobDataCampUser');
    const storedToken = localStorage.getItem('jobDataCampToken');
    
    if (storedUser && storedToken) {
      // Verify session with backend
      verifySession(storedToken, JSON.parse(storedUser));
    } else {
      setIsLoading(false);
    }
  }, [onAuthSuccess]);

  const verifySession = async (token, userData) => {
    try {
      const response = await fetch(`${BACKEND_URL}/auth/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_token: token })
      });

      const result = await response.json();
      
      if (result.success) {
        setUser(userData);
        onAuthSuccess(userData);
      } else {
        // Session invalid, clear storage
        localStorage.removeItem('jobDataCampUser');
        localStorage.removeItem('jobDataCampToken');
      }
    } catch (error) {
      console.error('Session verification failed:', error);
      localStorage.removeItem('jobDataCampUser');
      localStorage.removeItem('jobDataCampToken');
    }
    setIsLoading(false);
  };

  const handlePasswordLogin = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!password) {
      setError('Please enter a password');
      return;
    }
    
    try {
      const response = await fetch(`${BACKEND_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password: password })
      });

      const result = await response.json();
      
      if (result.success) {
        const userData = {
          ...result.user,
          authenticated: true,
          timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('jobDataCampUser', JSON.stringify(userData));
        localStorage.setItem('jobDataCampToken', result.session_token);
        setUser(userData);
        onAuthSuccess(userData);
        setPassword('');
      } else {
        setError(result.message || 'Authentication failed');
        onAuthFailure(result.message);
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Unable to connect to server. Please try again.');
      onAuthFailure('Connection error');
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError('');
    
    if (changePasswordData.newPassword !== changePasswordData.confirmPassword) {
      setError('New passwords do not match');
      return;
    }
    
    if (changePasswordData.newPassword.length < 4) {
      setError('New password must be at least 4 characters long');
      return;
    }
    
    try {
      const response = await fetch(`${BACKEND_URL}/admin/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: changePasswordData.currentPassword,
          new_password: changePasswordData.newPassword
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setError('');
        setShowChangePassword(false);
        setChangePasswordData({
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        });
        alert('Password changed successfully!');
      } else {
        setError(result.message || 'Password change failed');
      }
    } catch (error) {
      console.error('Password change error:', error);
      setError('Unable to change password. Please try again.');
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem('jobDataCampUser');
    localStorage.removeItem('jobDataCampToken');
    setUser(null);
    setError('');
    setPassword('');
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
          <span className="user-email">Admin Access</span>
          <div className="user-actions">
            <button 
              onClick={() => setShowChangePassword(!showChangePassword)} 
              className="change-password-btn"
            >
              Change Password
            </button>
            <button onClick={handleSignOut} className="sign-out-btn">
              Sign Out
            </button>
          </div>
        </div>
        
        {showChangePassword && (
          <div className="change-password-form">
            <h4>Change Admin Password</h4>
            <form onSubmit={handleChangePassword}>
              <input
                type="password"
                placeholder="Current Password"
                value={changePasswordData.currentPassword}
                onChange={(e) => setChangePasswordData({
                  ...changePasswordData,
                  currentPassword: e.target.value
                })}
                required
              />
              <input
                type="password"
                placeholder="New Password"
                value={changePasswordData.newPassword}
                onChange={(e) => setChangePasswordData({
                  ...changePasswordData,
                  newPassword: e.target.value
                })}
                required
              />
              <input
                type="password"
                placeholder="Confirm New Password"
                value={changePasswordData.confirmPassword}
                onChange={(e) => setChangePasswordData({
                  ...changePasswordData,
                  confirmPassword: e.target.value
                })}
                required
              />
              <div className="form-actions">
                <button type="submit" className="submit-btn">Change Password</button>
                <button 
                  type="button" 
                  onClick={() => setShowChangePassword(false)}
                  className="cancel-btn"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>Secure Access Portal</h2>
          <p>Sign in to use TS EAPCET practice exams and job search tools</p>
        </div>
        
        <div className="auth-content">
          <div className="restriction-notice">
            <span className="lock-icon">LOCK</span>
            <p><strong>Admin Access:</strong> Enter password to access the system</p>
          </div>
          
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
            </div>
          )}
          
          <form onSubmit={handlePasswordLogin} className="password-form">
            <div className="password-input-group">
              <input
                type="password"
                placeholder="Enter Admin Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="password-input"
                required
              />
              <button type="submit" className="login-btn">
                <span className="login-icon">KEY</span>
                Sign In
              </button>
            </div>
          </form>
          
          <div className="auth-info">
            <h4>System Features</h4>
            <ul>
              <li>10 full-length TS EAPCET engineering mock papers</li>
              <li>Detailed solution sheets with explanations for each exam</li>
              <li>Official-pattern exam instructions and subject distribution</li>
              <li>Advanced job search with H1B prediction tools</li>
              <li>Secure password-based authentication</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Auth;