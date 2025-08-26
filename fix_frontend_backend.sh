#!/bin/bash

echo "🔧 JobDataCamp Frontend-Backend Fix"
echo "===================================="

# Stop any existing React processes
echo "🛑 Stopping existing React processes..."
pkill -f "npm start" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
sleep 2

# Verify backend is working
echo -e "\n🧪 Testing backend connectivity..."
BACKEND_STATUS=$(curl -s https://python-job-scraper.onrender.com/health)
if echo "$BACKEND_STATUS" | grep -q "healthy"; then
    echo "✅ Backend is responding correctly"
else
    echo "❌ Backend is not responding. Please check Render deployment."
    exit 1
fi

# Navigate to frontend directory
cd /workspace/full_stack/frontend

# Verify .env file exists and has correct configuration
echo -e "\n📁 Checking frontend configuration..."
if [ ! -f .env ]; then
    echo "⚠️  .env file missing. Creating with PRODUCTION configuration..."
    cat > .env << EOF
# Frontend Configuration for JobDataCamp
# Production backend URL (Render.com deployment)
REACT_APP_BACKEND_URL=https://python-job-scraper.onrender.com

# API timeout
REACT_APP_API_TIMEOUT=120000

# Environment indicator
REACT_APP_ENVIRONMENT=production

# Development override (uncomment for local development)
# REACT_APP_BACKEND_URL=http://localhost:5000
# REACT_APP_ENVIRONMENT=development
EOF
    echo "✅ Created .env file with PRODUCTION configuration (Render.com backend)"
else
    echo "✅ .env file exists"
    # Verify it has the production URL
    if grep -q "python-job-scraper.onrender.com" .env; then
        echo "✅ .env configured for PRODUCTION backend (Render.com)"
    else
        echo "⚠️  .env may not be configured for production. Updating..."
        sed -i 's|REACT_APP_BACKEND_URL=.*|REACT_APP_BACKEND_URL=https://python-job-scraper.onrender.com|g' .env
        echo "✅ Updated .env to use PRODUCTION backend"
    fi
fi

# Show current configuration
echo -e "\n📋 Current configuration:"
cat .env | grep REACT_APP_BACKEND_URL | head -1

# Clear React cache to ensure environment variables are picked up
echo -e "\n🧹 Clearing React cache..."
rm -rf node_modules/.cache/ 2>/dev/null || true
rm -rf .env.local 2>/dev/null || true

# Install dependencies if needed
if [ ! -d node_modules ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start React app
echo -e "\n🚀 Starting React development server..."
echo "📱 Frontend will be available at: http://localhost:3000"
echo "🔧 Backend is running at: https://python-job-scraper.onrender.com"
echo ""
echo "🔍 After startup, check for:"
echo "  • Green dot in bottom-right corner (backend connected)"
echo "  • No console errors related to backend connectivity"
echo "  • Successful TAMU authentication"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"

# Start the React app
npm start