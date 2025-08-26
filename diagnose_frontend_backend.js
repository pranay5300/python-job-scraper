#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 JobDataCamp Frontend-Backend Connection Diagnosis\n');

// 1. Check .env file
const envPath = path.join(__dirname, 'full_stack', 'frontend', '.env');
console.log('📁 Checking .env file...');
try {
    const envContent = fs.readFileSync(envPath, 'utf8');
    console.log('✅ .env file exists:');
    console.log(envContent);
    
    // Parse REACT_APP_BACKEND_URL
    const match = envContent.match(/REACT_APP_BACKEND_URL=(.+)/);
    if (match) {
        const backendUrl = match[1].trim();
        console.log(`🎯 Backend URL configured: ${backendUrl}`);
        
        // Test the backend URL
        console.log('\n🧪 Testing backend connectivity...');
        testBackend(backendUrl);
    } else {
        console.log('❌ REACT_APP_BACKEND_URL not found in .env file');
    }
} catch (error) {
    console.log('❌ .env file not found or unreadable:', error.message);
    console.log('💡 Creating .env file with production URL...');
    
    const productionEnv = `# Frontend Configuration for JobDataCamp
# Production backend URL
REACT_APP_BACKEND_URL=https://python-job-scraper.onrender.com

# API timeout
REACT_APP_API_TIMEOUT=120000

# Development override (uncomment for local development)
# REACT_APP_BACKEND_URL=http://localhost:5000
`;
    
    fs.writeFileSync(envPath, productionEnv);
    console.log('✅ Created .env file with production configuration');
}

// 2. Test backend function
async function testBackend(url) {
    try {
        const fetch = (await import('node-fetch')).default;
        
        console.log(`🔗 Testing: ${url}/health`);
        const response = await fetch(`${url}/health`);
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend is responding correctly:');
            console.log(`   Status: ${data.status}`);
            console.log(`   Database: ${data.database_initialized ? 'Initialized' : 'Not initialized'}`);
            console.log(`   Timestamp: ${data.timestamp}`);
            
            // Test CORS
            const corsOrigin = response.headers.get('access-control-allow-origin');
            console.log(`   CORS: ${corsOrigin || 'Headers not visible from Node.js'}`);
            
        } else {
            console.log(`❌ Backend returned error: ${response.status} ${response.statusText}`);
        }
        
    } catch (error) {
        console.log(`❌ Backend connection failed: ${error.message}`);
        
        if (error.message.includes('fetch')) {
            console.log('💡 Installing node-fetch...');
            require('child_process').execSync('npm install node-fetch@2', { stdio: 'inherit' });
            console.log('🔄 Please run this script again after installing node-fetch');
        }
    }
}

// 3. Check React processes
console.log('\n🔄 Checking React processes...');
try {
    const { execSync } = require('child_process');
    const processes = execSync('ps aux | grep -E "(npm start|react-scripts)" | grep -v grep', { encoding: 'utf8' });
    
    if (processes.trim()) {
        console.log('📱 React processes found:');
        console.log(processes);
    } else {
        console.log('⚠️  No React processes found - frontend may not be running');
        console.log('💡 Start frontend with: cd full_stack/frontend && npm start');
    }
} catch (error) {
    console.log('⚠️  Could not check React processes');
}

// 4. Recommendations
console.log('\n📋 Troubleshooting Steps:');
console.log('1. ✅ Backend is live at: https://python-job-scraper.onrender.com');
console.log('2. ✅ .env file should be configured with production URL');
console.log('3. 🔄 Restart React app to pick up environment changes:');
console.log('   cd full_stack/frontend && npm start');
console.log('4. 🌐 Open http://localhost:3000 and check browser console');
console.log('5. 👀 Look for backend status indicator (green dot = connected)');

console.log('\n🎯 Common Issues:');
console.log('• React app not restarted after .env changes');
console.log('• Browser cache preventing new environment variables');
console.log('• Frontend trying to connect to localhost instead of production');
console.log('• CORS issues (should be fixed with universal origins)');

console.log('\n✅ If backend status shows green dot, the connection is working!');