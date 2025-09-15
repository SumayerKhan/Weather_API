"""
Weather API Test Script
-----------------------
This script tests all endpoints of the Weather Data API.
Make sure your Flask app is running on http://127.0.0.1:5000 before running this script.
"""

import requests
import json
from datetime import datetime

# Base URL of your Flask API
BASE_URL = "http://127.0.0.1:5000"

def test_homepage():
    """Test the homepage endpoint"""
    print("=" * 50)
    print("Testing Homepage (GET /)")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type')}")
        print("✓ Homepage accessible")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error accessing homepage: {e}")

def test_single_temperature():
    """Test getting temperature for a specific station and date"""
    print("\n" + "=" * 50)
    print("Testing Single Temperature (GET /api/v1/<station>/<date>)")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {"station": "10", "date": "1998-10-15"},
        {"station": "1", "date": "2000-01-01"},
        {"station": "10", "date": "1999-12-31"},  # Test different date
    ]
    
    for case in test_cases:
        try:
            url = f"{BASE_URL}/api/v1/{case['station']}/{case['date']}"
            print(f"\nTesting: {url}")
            
            response = requests.get(url)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                # Validate response structure
                required_keys = ["station", "date", "temperature"]
                if all(key in data for key in required_keys):
                    print("✓ Response has all required fields")
                    if data["temperature"] is not None:
                        print(f"✓ Temperature: {data['temperature']}°C")
                    else:
                        print("! No temperature data for this date")
                else:
                    print("✗ Response missing required fields")
            else:
                print(f"✗ Request failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error: {e}")

def test_all_station_data():
    """Test getting all data for a station"""
    print("\n" + "=" * 50)
    print("Testing All Station Data (GET /api/v1/<station>)")
    print("=" * 50)
    
    stations_to_test = ["10", "1", "2"]
    
    for station in stations_to_test:
        try:
            url = f"{BASE_URL}/api/v1/{station}"
            print(f"\nTesting: {url}")
            
            response = requests.get(url)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Retrieved {len(data)} records")
                
                if len(data) > 0:
                    # Show first few records
                    print("First 3 records:")
                    for i, record in enumerate(data[:3]):
                        print(f"  {i+1}. {record}")
                    
                    # Show some statistics
                    temperatures = [r.get('   TG', 0) for r in data if r.get('   TG') != -9999]
                    if temperatures:
                        avg_temp = sum(temperatures) / len(temperatures) / 10  # Convert to Celsius
                        print(f"✓ Average temperature: {avg_temp:.1f}°C")
                else:
                    print("! No data found for this station")
            else:
                print(f"✗ Request failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error: {e}")

def test_annual_data():
    """Test getting annual data for a station"""
    print("\n" + "=" * 50)
    print("Testing Annual Data (GET /api/v1/annual/<station>/<year>)")
    print("=" * 50)
    
    test_cases = [
        {"station": "10", "year": "1988"},
        {"station": "10", "year": "1999"},
        {"station": "1", "year": "2000"},
    ]
    
    for case in test_cases:
        try:
            url = f"{BASE_URL}/api/v1/annual/{case['station']}/{case['year']}"
            print(f"\nTesting: {url}")
            
            response = requests.get(url)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Retrieved {len(data)} records for year {case['year']}")
                
                if len(data) > 0:
                    # Show date range
                    dates = [record.get('    DATE', '') for record in data]
                    if dates:
                        print(f"  Date range: {min(dates)} to {max(dates)}")
                    
                    # Count valid temperatures
                    valid_temps = [r for r in data if r.get('   TG', -9999) != -9999]
                    print(f"  Valid temperature readings: {len(valid_temps)}")
                else:
                    print(f"! No data found for station {case['station']} in year {case['year']}")
            else:
                print(f"✗ Request failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error: {e}")

def test_error_cases():
    """Test error handling"""
    print("\n" + "=" * 50)
    print("Testing Error Cases")
    print("=" * 50)
    
    error_tests = [
        {"url": f"{BASE_URL}/api/v1/99999/2000-01-01", "description": "Non-existent station"},
        {"url": f"{BASE_URL}/api/v1/10/invalid-date", "description": "Invalid date format"},
        {"url": f"{BASE_URL}/api/v1/abc/2000-01-01", "description": "Invalid station ID"},
    ]
    
    for test in error_tests:
        try:
            print(f"\nTesting: {test['description']}")
            print(f"URL: {test['url']}")
            
            response = requests.get(test['url'])
            print(f"Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"✓ Expected error response received")
            else:
                print(f"! Unexpected success: {response.json()}")
                
        except requests.exceptions.RequestException as e:
            print(f"✓ Request failed as expected: {e}")

def main():
    """Run all tests"""
    print("Weather Data API Test Suite")
    print(f"Testing API at: {BASE_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if API is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✓ API is accessible")
    except requests.exceptions.RequestException:
        print("✗ API is not accessible. Make sure your Flask app is running!")
        return
    
    # Run all tests
    test_homepage()
    test_single_temperature()
    test_all_station_data()
    test_annual_data()
    test_error_cases()
    
    print("\n" + "=" * 50)
    print("Test Suite Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()