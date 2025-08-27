import React, { useState, useEffect, useCallback } from 'react';

const BackendStatus = () => {
  const [status, setStatus] = useState('checking');
  const [message, setMessage] = useState('Checking backend status...');

  const checkBackendStatus = useCallback(async () => {
    try {
      // Use production backend (Render.com deployment)
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'https://python-job-scraper.onrender.com';
      
      // Log for debugging
      console.log('BackendStatus: Checking backend at:', backendUrl);
      
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${backendUrl}/health`, {
        method: 'GET',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        setStatus('online');
        setMessage(`✅ Backend online - ${data.status}`);
      } else {
        setStatus('error');
        setMessage(`⚠️ Backend responding but with errors (${response.status})`);
      }
    } catch (error) {
      setStatus('offline');
      
      if (error.name === 'AbortError') {
        setMessage('⏱️ Backend connection timeout');
      } else if (error.message.includes('Failed to fetch') || error.message.includes('ERR_CONNECTION_REFUSED')) {
        setMessage('🔧 Backend server offline');
      } else {
        setMessage(`❌ Connection error: ${error.message}`);
      }
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    let interval;
    
    const safeCheckStatus = async () => {
      if (isMounted) {
        try {
          await checkBackendStatus();
        } catch (error) {
          console.warn('Backend status check failed:', error);
          if (isMounted) {
            setStatus('offline');
            setMessage('❌ Connection check failed');
          }
        }
      }
    };

    // Initial check
    safeCheckStatus();
    
    // Check status every 30 seconds
    interval = setInterval(safeCheckStatus, 30000);
    
    return () => {
      isMounted = false;
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [checkBackendStatus]);

  const getStatusColor = () => {
    switch (status) {
      case 'online': return '#10b981';
      case 'offline': return '#ef4444';
      case 'error': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const handleStartServers = () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'https://python-job-scraper.onrender.com';
    
    const instructions = `PRODUCTION BACKEND STATUS (Render.com):

Backend URL: ${backendUrl}

If you're seeing connection issues:
1. Render service may be starting up (cold start delay)
2. Check if the production backend is online
3. Verify CORS settings allow your domain
4. Check browser console for detailed errors
5. Wait 10-15 seconds and try refreshing the page

The backend is deployed on Render.com which may have cold start delays.

For local development:
1. Update .env file to use: REACT_APP_BACKEND_URL=http://localhost:5000
2. Start local backend with: ./start_servers.sh`;
    
    alert(instructions);
  };

  return (
    <div className="backend-status">
      <div className="status-indicator">
        <span 
          className="status-dot" 
          style={{ backgroundColor: getStatusColor() }}
        ></span>
        <span className="status-text">{message}</span>
        {status === 'offline' && (
          <button onClick={handleStartServers} className="start-server-btn">
            Start Servers
          </button>
        )}
        <button onClick={checkBackendStatus} className="refresh-btn">
          🔄
        </button>
      </div>
    </div>
  );
};

export default BackendStatus;