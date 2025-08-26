import React, { useState, useEffect } from 'react';

const BackendStatus = () => {
  const [status, setStatus] = useState('checking');
  const [message, setMessage] = useState('Checking backend status...');

  const checkBackendStatus = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';
      const response = await fetch(`${backendUrl}/health`, {
        method: 'GET',
        timeout: 5000
      });
      
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
      if (error.message.includes('Failed to fetch') || error.message.includes('ERR_CONNECTION_REFUSED')) {
        setMessage('🔧 Backend server offline');
      } else {
        setMessage(`❌ Connection error: ${error.message}`);
      }
    }
  };

  useEffect(() => {
    checkBackendStatus();
    // Check status every 30 seconds
    const interval = setInterval(checkBackendStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (status) {
      case 'online': return '#10b981';
      case 'offline': return '#ef4444';
      case 'error': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const handleStartServers = () => {
    const instructions = `To start the backend server:

1. Open a terminal
2. Run: cd /workspace && ./start_servers.sh
3. Wait for "✅ Backend started successfully" message
4. Refresh this page

Or manually:
1. cd /workspace/full_stack/backend
2. python3 app.py

The backend should then be available at http://localhost:5000`;

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