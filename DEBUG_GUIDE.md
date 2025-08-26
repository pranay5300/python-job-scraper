# 🔧 JobDataCamp Debugging Guide

## Quick Start (Recommended)

```bash
# One-command startup
cd /workspace && ./start_servers.sh
```

This script will:
- ✅ Kill existing processes
- ✅ Install missing dependencies
- ✅ Start backend on port 5000
- ✅ Start frontend on port 3000
- ✅ Provide status monitoring

## Common Issues & Solutions

### 1. 🚫 ERR_CONNECTION_REFUSED (Backend Not Running)

**Symptoms:**
- `GET http://localhost:5000/download_excel ... net::ERR_CONNECTION_REFUSED`
- Backend status shows "🔧 Backend server offline"

**Solutions:**

#### Option A: Automatic Startup
```bash
cd /workspace && ./start_servers.sh
```

#### Option B: Manual Backend Start
```bash
cd /workspace/full_stack/backend
python3 app.py
```

#### Option C: Install Dependencies First
```bash
cd /workspace/full_stack/backend
pip3 install --break-system-packages pandas flask flask-cors openpyxl requests beautifulsoup4 numpy
python3 app.py
```

### 2. 📄 CSS MIME Type Errors

**Symptoms:**
- `Refused to apply style from 'https://www.jobdatacamp.com/index.css' because its MIME type ('text/plain') is not a supported stylesheet MIME type`

**Solution:** ✅ Fixed!
- Removed problematic external CSS references
- All styles now handled by React's built-in CSS system

### 3. 🔍 Missing Favicon (404 Error)

**Symptoms:**
- `/favicon.ico:1 Failed to load resource: the server responded with a status of 404`

**Solution:** ✅ Fixed!
- Added inline SVG favicon with briefcase emoji 💼
- No external files needed

### 4. 📱 External Script Errors

**Symptoms:**
- `Unknown action: is-mobile`
- `Page data capture skipped`
- Fullstory sampling errors

**Solution:** ✅ Fixed!
- Removed all external JotForm scripts
- Clean HTML without external dependencies

### 5. 🔐 Authentication Issues

**Symptoms:**
- Can't access job search interface
- Authentication stuck in loading

**Solutions:**

#### Clear Browser Storage
```javascript
// Run in browser console
localStorage.clear();
location.reload();
```

#### Test Authentication
- Use any @tamu.edu email (e.g., `student@tamu.edu`)
- Non-TAMU emails will be rejected

### 6. 📊 H1B Predictions Not Working

**Symptoms:**
- No H1B column in Excel file
- H1B checkbox not visible

**Check:**
1. ✅ H1B checkbox is checked
2. ✅ Backend is running
3. ✅ include_h1b=true in URL parameters

## System Status Monitoring

### Backend Health Check
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database_initialized": true,
  "timestamp": "2024-01-XX..."
}
```

### Frontend Status
- Look for backend status indicator in bottom-right corner
- Green dot = Backend online
- Red dot = Backend offline
- Yellow dot = Backend error

## Port Usage

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 5000 | http://localhost:5000 |

### Check Port Usage
```bash
# Check if ports are in use
netstat -tuln | grep :3000
netstat -tuln | grep :5000

# Kill processes on specific ports
sudo lsof -ti:5000 | xargs kill -9
sudo lsof -ti:3000 | xargs kill -9
```

## File Structure Check

```
/workspace/
├── start_servers.sh          # ✅ Startup script
└── full_stack/
    ├── backend/
    │   ├── app.py            # ✅ Main backend
    │   ├── requirements.txt  # ✅ Dependencies
    │   └── backend.log       # 📝 Backend logs
    └── frontend/
        ├── .env              # ✅ Environment config
        ├── .env.example      # ✅ Config template
        └── src/
            ├── App.js        # ✅ Main app with auth
            ├── App.css       # ✅ All styles
            └── components/
                ├── Auth.js         # ✅ TAMU authentication
                ├── JobForm.js      # ✅ Job search form
                ├── Header.js       # ✅ TAMU header
                └── BackendStatus.js # ✅ Status monitor
```

## Testing Checklist

### ✅ Backend Tests
- [ ] `python3 app.py` starts without errors
- [ ] `curl http://localhost:5000/health` returns 200
- [ ] Database initializes with sample jobs
- [ ] H1B predictions work

### ✅ Frontend Tests
- [ ] `npm start` opens browser automatically
- [ ] Authentication screen appears
- [ ] TAMU email validation works
- [ ] Job search form loads after auth
- [ ] H1B checkbox is visible and functional
- [ ] Backend status indicator shows green

### ✅ Integration Tests
- [ ] Job search completes successfully
- [ ] Excel file downloads
- [ ] H1B predictions included when enabled
- [ ] Error handling works when backend is offline

## Log Files

### Backend Logs
```bash
tail -f /workspace/full_stack/backend/backend.log
```

### Frontend Logs
- Check browser console (F12)
- Look for network errors in Network tab

## Environment Variables

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:5000
REACT_APP_API_TIMEOUT=120000
```

### Backend (optional)
```env
FLASK_ENV=development
LOG_LEVEL=INFO
```

## Emergency Reset

### Complete System Reset
```bash
# Stop all processes
pkill -f "python3 app.py"
pkill -f "npm start"

# Clean up
cd /workspace/full_stack/backend
rm -f backend.log fast_jobs.db

cd /workspace/full_stack/frontend
rm -rf node_modules .env

# Restart
cd /workspace && ./start_servers.sh
```

### Browser Reset
```javascript
// Run in browser console
localStorage.clear();
sessionStorage.clear();
location.reload();
```

## Support

### Quick Diagnostics
1. Run `./start_servers.sh` 
2. Check backend status indicator
3. Test with valid @tamu.edu email
4. Try job search with H1B enabled

### Need Help?
- Check this debugging guide first
- Look at browser console errors
- Check backend logs
- Verify all files are present in expected locations

### System Requirements
- ✅ Python 3.8+
- ✅ Node.js 14+
- ✅ Modern web browser
- ✅ Network access for dependencies

---

**Last Updated:** Current version includes all fixes for CSS MIME types, favicon, external scripts, and connection issues.