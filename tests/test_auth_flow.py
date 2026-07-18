import requests
import json
from pathlib import Path
import sys

# Fix encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TESTING KNOWMATE BACKEND - FULL AUTH FLOW")
print("=" * 60)

# 1. TEST REGISTRATION
print("\n1. TESTING REGISTRATION...")
register_data = {
    "company_name": "TestCorp",
    "admin": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@test.com",
        "password": "TestPass123!"
    }
}

try:
    response = requests.post(f"{BASE_URL}/companies/register", json=register_data, timeout=5)
    if response.status_code == 200:
        print("[OK] REGISTRATION SUCCESS")
        result = response.json()
        print(f"  Message: {result.get('message')}")
        print(f"  Company ID: {result.get('company_id')}")
    else:
        print(f"[FAIL] REGISTRATION FAILED: {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"[ERROR] {e}")

# 2. GET VERIFICATION TOKEN
print("\n2. CHECKING VERIFICATION TOKEN...")
token_file = Path("latest_verification_link.txt")
if token_file.exists():
    content = token_file.read_text()
    print(f"[OK] Token file exists")
    print(f"  Content preview: {content[:100]}...")
    
    # Extract token from URL
    if "token=" in content:
        token = content.split("token=")[1].split(" ")[0].split("\n")[0]
        print(f"  Extracted token: {token[:20]}...")
        
        # 3. TEST VERIFICATION
        print("\n3. TESTING EMAIL VERIFICATION...")
        try:
            verify_response = requests.get(f"{BASE_URL}/companies/verify", params={"token": token}, timeout=5)
            if verify_response.status_code == 200:
                print("[OK] VERIFICATION SUCCESS")
                print(f"  Response: {verify_response.json()}")
            else:
                print(f"[FAIL] VERIFICATION FAILED: {verify_response.status_code}")
                print(f"  Response: {verify_response.text}")
        except Exception as e:
            print(f"[ERROR] {e}")
else:
    print("[FAIL] Token file not found - registration may have failed")

# 4. TEST LOGIN
print("\n4. TESTING LOGIN...")
login_data = {
    "username": "john@test.com",
    "password": "TestPass123!"
}

try:
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data, timeout=5)
    if login_response.status_code == 200:
        print("[OK] LOGIN SUCCESS")
        login_result = login_response.json()
        access_token = login_result.get("access_token")
        print(f"  Token type: {login_result.get('token_type')}")
        print(f"  Access token: {access_token[:30]}...")
        
        # 5. TEST GET CURRENT USER
        print("\n5. TESTING GET CURRENT USER...")
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=5)
            if me_response.status_code == 200:
                print("[OK] GET CURRENT USER SUCCESS")
                user_data = me_response.json()
                print(f"  Email: {user_data.get('email')}")
                print(f"  First name: {user_data.get('first_name')}")
                print(f"  Last name: {user_data.get('last_name')}")
            else:
                print(f"[FAIL] GET USER FAILED: {me_response.status_code}")
                print(f"  Response: {me_response.text}")
        except Exception as e:
            print(f"[ERROR] {e}")
    else:
        print(f"[FAIL] LOGIN FAILED: {login_response.status_code}")
        print(f"  Response: {login_response.text}")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
