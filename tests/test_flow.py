#!/usr/bin/env python3
"""
Complete test of the registration and login flow.
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test 1: Register a new company"""
    print("\n=== TEST 1: Company Registration ===")
    payload = {
        "company_name": "TestCorp2",
        "admin": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john2@test.com",
            "password": "TestPass123!"
        }
    }
    try:
        res = requests.post(f"{BASE_URL}/companies/register", json=payload, timeout=10)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        return res.status_code == 201
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_verify():
    """Test 2: Verify the registration"""
    print("\n=== TEST 2: Company Verification ===")
    # Read the token from the file
    try:
        with open("latest_verification_link.txt", "r") as f:
            link = f.read().strip()
            # Extract token from link
            token = link.split("token=")[-1]
            print(f"Token: {token}")
    except Exception as e:
        print(f"ERROR reading token: {e}")
        return False
    
    try:
        res = requests.get(f"{BASE_URL}/companies/verify", params={"token": token}, timeout=10)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        return res.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_login():
    """Test 3: Login with the verified account"""
    print("\n=== TEST 3: Login ===")
    payload = {
        "username": "john2@test.com",
        "password": "TestPass123!"
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/login", data=payload, timeout=10)
        print(f"Status: {res.status_code}")
        data = res.json()
        print(f"Response: {data}")
        if res.status_code == 200:
            token = data.get("access_token")
            print(f"Token: {token[:20]}...")
            return token
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def test_get_me(token):
    """Test 4: Get current user profile"""
    print("\n=== TEST 4: Get Current User ===")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        res = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        return res.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    print("Starting comprehensive flow test...")
    print("=" * 50)
    
    # Test 1
    if not test_registration():
        print("\n❌ Registration FAILED")
        sys.exit(1)
    print("\n✅ Registration passed")
    
    time.sleep(1)
    
    # Test 2
    if not test_verify():
        print("\n❌ Verification FAILED")
        sys.exit(1)
    print("\n✅ Verification passed")
    
    time.sleep(1)
    
    # Test 3
    token = test_login()
    if not token:
        print("\n❌ Login FAILED")
        sys.exit(1)
    print("\n✅ Login passed")
    
    time.sleep(1)
    
    # Test 4
    if not test_get_me(token):
        print("\n❌ Get me FAILED")
        sys.exit(1)
    print("\n✅ Get me passed")
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
