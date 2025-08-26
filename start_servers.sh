#!/bin/bash

echo "🚀 Starting JobDataCamp Servers..."

# Function to check if port is in use
check_port() {
    netstat -tuln | grep ":$1 " > /dev/null
    return $?
}

# Kill existing processes on ports 3000 and 5000
echo "🧹 Cleaning up existing processes..."
pkill -f "python3 app.py" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
sleep 2

# Start Backend Server
echo "🔧 Starting Backend Server on port 5000..."
cd /workspace/full_stack/backend

# Install dependencies if needed
if ! python3 -c "import pandas" 2>/dev/null; then
    echo "📦 Installing backend dependencies..."
    pip3 install --break-system-packages pandas flask flask-cors openpyxl requests beautifulsoup4 numpy
fi

# Start backend in background
nohup python3 app.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if check_port 5000; then
        echo "✅ Backend started successfully on port 5000 (PID: $BACKEND_PID)"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start after 30 seconds"
        exit 1
    fi
done

# Start Frontend Server
echo "🎨 Starting Frontend Server on port 3000..."
cd /workspace/full_stack/frontend

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Install dependencies if needed
if [ ! -d node_modules ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend
echo "🚀 Starting React development server..."
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 Servers started successfully!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:5000"
echo "📊 Backend Health: http://localhost:5000/health"
echo ""
echo "🔍 To monitor logs:"
echo "   Backend:  tail -f /workspace/full_stack/backend/backend.log"
echo "   Frontend: Check the terminal output"
echo ""
echo "🛑 To stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 5
echo "✅ All servers should be running now!"
echo "🎓 Access TAMU JobDataCamp at: http://localhost:3000"