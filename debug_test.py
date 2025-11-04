#!/usr/bin/env python3
"""
Debug script to test the backend connection and data insertion
"""
import requests
import json

def test_signup():
    base_url = "http://127.0.0.1:8000"
    
    # Test data
    test_data = {
        "name": "Debug Test User",
        "phone": "9876543210",
        "email": "debug@test.com",
        "password": "testpass123"
    }
    
    print("Testing signup endpoint...")
    print(f"Sending data: {test_data}")
    
    try:
        response = requests.post(f"{base_url}/signup", data=test_data)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Success! User created with ID: {data.get('user_id')}")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw error: {response.text}")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_signup()
