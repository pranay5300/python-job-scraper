// Test script to verify frontend can connect to production backend
const backendUrl = 'https://python-job-scraper.onrender.com';

console.log('🧪 Testing Frontend → Backend Connection');
console.log('Backend URL:', backendUrl);

// Test 1: Health Check
async function testHealthEndpoint() {
  try {
    console.log('\n📋 Test 1: Health Check');
    const response = await fetch(`${backendUrl}/health`);
    const data = await response.json();
    console.log('✅ Health Check Response:', data);
    return true;
  } catch (error) {
    console.log('❌ Health Check Failed:', error.message);
    return false;
  }
}

// Test 2: H1B Prediction
async function testH1BEndpoint() {
  try {
    console.log('\n📋 Test 2: H1B Prediction');
    const response = await fetch(`${backendUrl}/test_h1b?company=Google&role=Software%20Engineer`);
    const data = await response.json();
    console.log('✅ H1B Prediction Response:', data);
    return true;
  } catch (error) {
    console.log('❌ H1B Prediction Failed:', error.message);
    return false;
  }
}

// Test 3: Job Search (GET request simulation)
async function testJobSearchEndpoint() {
  try {
    console.log('\n📋 Test 3: Job Search Parameters');
    const params = new URLSearchParams({
      companies: JSON.stringify([{"company": "Google", "weight": 100}]),
      roles: JSON.stringify([{"role": "Software Engineer", "weight": 100}]),
      locations: JSON.stringify([{"location": "California", "weight": 100}]),
      overall_company_weight: 33,
      overall_role_weight: 33,
      overall_location_weight: 34,
      include_h1b: 'true',
      job_type: 'Full-Time'
    });

    const url = `${backendUrl}/download_excel?${params}`;
    console.log('🔗 Job Search URL:', url);
    
    const response = await fetch(url, { method: 'HEAD' }); // HEAD request to test without downloading
    console.log(`✅ Job Search Endpoint Status: ${response.status} ${response.statusText}`);
    return response.ok;
  } catch (error) {
    console.log('❌ Job Search Test Failed:', error.message);
    return false;
  }
}

// Run all tests
async function runAllTests() {
  console.log('🚀 Starting Backend Connection Tests...\n');
  
  const test1 = await testHealthEndpoint();
  const test2 = await testH1BEndpoint();
  const test3 = await testJobSearchEndpoint();
  
  console.log('\n📊 Test Results Summary:');
  console.log('Health Check:', test1 ? '✅ PASS' : '❌ FAIL');
  console.log('H1B Prediction:', test2 ? '✅ PASS' : '❌ FAIL');
  console.log('Job Search:', test3 ? '✅ PASS' : '❌ FAIL');
  
  const allPassed = test1 && test2 && test3;
  console.log('\n🎯 Overall Result:', allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED');
  
  if (allPassed) {
    console.log('\n🎉 Frontend is ready to connect to production backend!');
    console.log('💡 Make sure your .env file has: REACT_APP_BACKEND_URL=' + backendUrl);
  } else {
    console.log('\n🔧 Check backend status and CORS configuration.');
  }
}

// Run tests if this script is executed directly
if (typeof window === 'undefined') {
  runAllTests();
}

// Export for browser use
if (typeof module !== 'undefined') {
  module.exports = { runAllTests, testHealthEndpoint, testH1BEndpoint, testJobSearchEndpoint };
}