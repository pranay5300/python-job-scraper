#!/usr/bin/env python3
"""
Test script for JobDataCamp API
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_stats():
    """Test stats endpoint"""
    print("\n📊 Testing stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            print("✅ Stats retrieved successfully")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")

def test_h1b_prediction():
    """Test H1B prediction endpoint"""
    print("\n🛂 Testing H1B prediction...")
    test_cases = [
        ("Google", "Software Engineer"),
        ("Microsoft", "Data Scientist"),
        ("Startup Inc", "Customer Service"),
        ("Amazon", "Product Manager")
    ]
    
    for company, role in test_cases:
        try:
            params = {"company": company, "role": role}
            response = requests.get(f"{BASE_URL}/test_h1b", params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {company} - {role}: {data['h1b_probability']}")
            else:
                print(f"❌ Failed for {company} - {role}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error for {company} - {role}: {e}")

def test_job_search():
    """Test job search with Excel download"""
    print("\n💼 Testing job search with H1B predictions...")
    
    # Test parameters
    params = {
        "companies": json.dumps([{"company": "Google", "weight": 70}, {"company": "Microsoft", "weight": 30}]),
        "roles": json.dumps([{"role": "Software Engineer", "weight": 80}, {"role": "Data Scientist", "weight": 20}]),
        "locations": json.dumps([{"location": "San Francisco", "weight": 60}, {"location": "Seattle", "weight": 40}]),
        "overall_company_weight": 40,
        "overall_role_weight": 40,
        "overall_location_weight": 20,
        "job_type": "Full-Time",
        "include_h1b": "true"
    }
    
    try:
        print("🚀 Sending job search request...")
        start_time = time.time()
        
        response = requests.get(f"{BASE_URL}/download_excel", params=params, timeout=30)
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Job search completed in {elapsed_time:.2f} seconds")
            print(f"📁 Excel file size: {len(response.content)} bytes")
            print(f"📄 Content type: {response.headers.get('content-type', 'unknown')}")
            
            # Save the file for verification
            with open("test_job_results.xlsx", "wb") as f:
                f.write(response.content)
            print("💾 Results saved as 'test_job_results.xlsx'")
            
        else:
            print(f"❌ Job search failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"❌ Job search error: {e}")

def main():
    """Run all tests"""
    print("🧪 JobDataCamp API Test Suite")
    print("=" * 50)
    
    test_health()
    test_stats()
    test_h1b_prediction()
    test_job_search()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")

if __name__ == "__main__":
    main()