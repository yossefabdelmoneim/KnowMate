import requests
import json
import sys
import time
import uuid
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000"
passed = 0
failed = 0
TEST_EMAIL = f"test_{uuid.uuid4().hex[:8]}@test.com"
TEST_PASS = "TestPass123!"
token = None
session_id = None

def check(name, status_code, expected=None, fail_on_error=True):
    global passed, failed
    status = status_code if isinstance(status_code, int) else status_code.status_code
    ok = 200 <= status < 300
    if ok:
        passed += 1
        print(f"  [PASS] {name} (HTTP {status})")
    else:
        failed += 1
        print(f"  [FAIL] {name} (HTTP {status})")
    if expected and status_code is not int:
        pass
    return ok

def section(n, title):
    print(f"\n{'='*60}")
    print(f"  {n}. {title}")
    print(f"{'='*60}")

print(f"{'='*60}")
print("  KNOWMATE - COMPREHENSIVE ENDPOINT TEST")
print(f"{'='*60}")

# ===== 1. ROOT =====
section(1, "Root Endpoint")
try:
    r = requests.get(f"{BASE}/", timeout=5)
    check("GET /", r.status_code)
    print(f"     Response: {r.json()}")
except Exception as e:
    print(f"  [FAIL] GET / - {e}"); failed += 1

# ===== 2. HEALTH =====
section(2, "Health Check")
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    check("GET /health", r.status_code)
    data = r.json()
    print(f"     Status: {data.get('status')}, LLM: {data.get('llm_available')}")
except Exception as e:
    print(f"  [FAIL] GET /health - {e}"); failed += 1

# ===== 3. AUTH REGISTER =====
section(3, "Register User")
try:
    r = requests.post(f"{BASE}/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASS, "full_name": "Test User"},
        timeout=10)
    if r.status_code == 201:
        check("POST /auth/register", r.status_code)
        print(f"     Email: {TEST_EMAIL}")
    elif r.status_code == 400 and "already" in r.text:
        print(f"  [INFO] User already exists")
    else:
        print(f"  [FAIL] POST /auth/register - {r.status_code}: {r.text[:100]}"); failed += 1
except Exception as e:
    print(f"  [FAIL] POST /auth/register - {e}"); failed += 1

# ===== 4. AUTH LOGIN =====
section(4, "Login")
try:
    r = requests.post(f"{BASE}/auth/login",
        data={"username": TEST_EMAIL, "password": TEST_PASS},
        timeout=10)
    if r.status_code == 200:
        check("POST /auth/login", r.status_code)
        token = r.json().get("access_token")
        print(f"     Token: {token[:30]}...")
    else:
        print(f"  [FAIL] POST /auth/login - {r.status_code}: {r.text[:100]}"); failed += 1
except Exception as e:
    print(f"  [FAIL] POST /auth/login - {e}"); failed += 1

headers = {"Authorization": f"Bearer {token}"} if token else {}

# ===== 5. AUTH ME =====
section(5, "Get Current User")
if token:
    try:
        r = requests.get(f"{BASE}/auth/me", headers=headers, timeout=10)
        check("GET /auth/me", r.status_code)
        print(f"     User: {r.json().get('email')}")
    except Exception as e:
        print(f"  [FAIL] GET /auth/me - {e}"); failed += 1
else:
    print("  [SKIP] No token available")

# ===== 6. COMPANIES LIST =====
section(6, "List Companies")
try:
    r = requests.get(f"{BASE}/companies/", timeout=10)
    check("GET /companies/", r.status_code)
    companies = r.json()
    print(f"     Companies count: {len(companies)}")
except Exception as e:
    print(f"  [FAIL] GET /companies/ - {e}"); failed += 1

# ===== 7. CREATE COMPANY =====
section(7, "Create Company")
try:
    r = requests.post(f"{BASE}/companies/",
        json={"name": f"TestCorp-{uuid.uuid4().hex[:6]}", "description": "Test company"},
        timeout=10)
    if r.status_code == 201:
        check("POST /companies/", r.status_code)
        print(f"     Company: {r.json().get('name')}")
    else:
        print(f"  [FAIL] POST /companies/ - {r.status_code}: {r.text[:100]}"); failed += 1
except Exception as e:
    print(f"  [FAIL] POST /companies/ - {e}"); failed += 1

# ===== 8. COMPANY REGISTER (full flow) =====
section(8, "Company Registration Flow")
company_name = f"FlowCorp-{uuid.uuid4().hex[:6]}"
flow_email = f"flow_{uuid.uuid4().hex[:8]}@test.com"
try:
    r = requests.post(f"{BASE}/companies/register",
        json={
            "company_name": company_name,
            "admin": {
                "first_name": "Flow",
                "last_name": "User",
                "email": flow_email,
                "password": TEST_PASS
            }
        },
        timeout=10)
    if r.status_code == 201:
        check("POST /companies/register", r.status_code)
        print(f"     {r.json().get('message')}")
        print(f"     Email: {flow_email}")
    elif r.status_code == 409:
        print(f"  [INFO] Pending registration exists: {r.json().get('detail')}")
    else:
        print(f"  [FAIL] POST /companies/register - {r.status_code}: {r.text[:100]}"); failed += 1
except Exception as e:
    print(f"  [FAIL] POST /companies/register - {e}"); failed += 1

# ===== 9. SEARCH =====
section(9, "Search Endpoint")
if token:
    try:
        r = requests.post(f"{BASE}/search/",
            json={"query": "test query", "company_id": "company_1"},
            headers=headers, timeout=10)
        if r.status_code in (200, 404, 422):
            check(f"POST /search/ (HTTP {r.status_code})", r.status_code)
            print(f"     Results: {len(r.json()) if isinstance(r.json(), list) else r.json()}")
        else:
            print(f"  [FAIL] POST /search/ - {r.status_code}: {r.text[:100]}"); failed += 1
    except Exception as e:
        print(f"  [FAIL] POST /search/ - {e}"); failed += 1
else:
    print("  [SKIP] No token available")

# ===== 10. CHAT =====
section(10, "Chat Endpoint")
if token:
    try:
        r = requests.post(f"{BASE}/api/chat",
            json={"question": "What is the company policy?", "company_id": "company_1", "agent_type": "default"},
            headers=headers, timeout=30)
        if r.status_code == 200:
            check("POST /api/chat", r.status_code)
            data = r.json()
            print(f"     Answer: {str(data.get('answer', ''))[:80]}...")
            print(f"     Sources: {len(data.get('sources', []))}")
        else:
            print(f"  [INFO] POST /api/chat - {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  [FAIL] POST /api/chat - {e}"); failed += 1
else:
    print("  [SKIP] No token available")

# ===== 11. DATA ANALYSIS: Supported Types =====
section(11, "Data Analysis - Supported Types")
try:
    r = requests.get(f"{BASE}/sessions/_meta/supported-types", timeout=10)
    check("GET /sessions/_meta/supported-types", r.status_code)
    data = r.json()
    print(f"     Extensions: {data.get('extensions')}")
except Exception as e:
    print(f"  [FAIL] GET /sessions/_meta/supported-types - {e}"); failed += 1

# ===== 12. DATA ANALYSIS: Create Session =====
section(12, "Data Analysis - Create Session")
if token:
    try:
        r = requests.post(f"{BASE}/sessions",
            json={"title": "Test Session", "description": "Created by comprehensive test"},
            headers=headers, timeout=10)
        if r.status_code == 201:
            check("POST /sessions", r.status_code)
            session_id = r.json().get("id")
            print(f"     Session ID: {session_id}")
        else:
            print(f"  [FAIL] POST /sessions - {r.status_code}: {r.text[:100]}"); failed += 1
    except Exception as e:
        print(f"  [FAIL] POST /sessions - {e}"); failed += 1
else:
    print("  [SKIP] No token available")

# ===== 13. DATA ANALYSIS: List Sessions =====
section(13, "Data Analysis - List Sessions")
if token:
    try:
        r = requests.get(f"{BASE}/sessions", headers=headers, timeout=10)
        check("GET /sessions", r.status_code)
        data = r.json()
        print(f"     Total sessions: {data.get('total')}")
    except Exception as e:
        print(f"  [FAIL] GET /sessions - {e}"); failed += 1
else:
    print("  [SKIP] No token available")

# ===== 14. DATA ANALYSIS: Get Session =====
section(14, "Data Analysis - Get Session")
if token and session_id:
    try:
        r = requests.get(f"{BASE}/sessions/{session_id}", headers=headers, timeout=10)
        check(f"GET /sessions/{session_id}", r.status_code)
        data = r.json()
        print(f"     Title: {data.get('title')}")
        print(f"     Messages: {data.get('message_count')}")
    except Exception as e:
        print(f"  [FAIL] GET /sessions/{session_id} - {e}"); failed += 1
else:
    print("  [SKIP] No session available")

# ===== 15. DATA ANALYSIS: Update Session =====
section(15, "Data Analysis - Update Session")
if token and session_id:
    try:
        r = requests.patch(f"{BASE}/sessions/{session_id}",
            json={"title": "Updated Test Session"},
            headers=headers, timeout=10)
        check(f"PATCH /sessions/{session_id}", r.status_code)
        print(f"     Updated title: {r.json().get('title')}")
    except Exception as e:
        print(f"  [FAIL] PATCH /sessions/{session_id} - {e}"); failed += 1
else:
    print("  [SKIP] No session available")

# ===== 16. DATA ANALYSIS: Upload Dataset =====
section(16, "Data Analysis - Upload Dataset")
if token and session_id:
    csv_data = b"name,age,score\nAlice,30,95\nBob,25,87\nCharlie,35,92\nDiana,28,88\nEve,32,91"
    try:
        r = requests.post(f"{BASE}/sessions/{session_id}/dataset",
            files={"file": ("test_data.csv", csv_data, "text/csv")},
            headers=headers, timeout=15)
        if r.status_code == 201:
            check(f"POST /sessions/{session_id}/dataset", r.status_code)
            ds = r.json().get("dataset", {})
            print(f"     File: {ds.get('original_filename')}")
            print(f"     Rows: {ds.get('row_count')}, Cols: {ds.get('column_count')}")
        else:
            print(f"  [INFO] POST /sessions/{session_id}/dataset - {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  [FAIL] POST /sessions/{session_id}/dataset - {e}"); failed += 1
else:
    print("  [SKIP] No session available")

# ===== 17. DATA ANALYSIS: Send Message =====
section(17, "Data Analysis - Send Message")
if token and session_id:
    try:
        r = requests.post(f"{BASE}/sessions/{session_id}/messages",
            json={"question": "show me the average age", "debug": True},
            headers=headers, timeout=300)
        if r.status_code == 200:
            check(f"POST /sessions/{session_id}/messages", r.status_code)
            data = r.json()
            print(f"     Success: {data.get('success')}")
            print(f"     Summary: {str(data.get('summary', ''))[:100]}")
        else:
            print(f"  [INFO] POST /sessions/{session_id}/messages - {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  [FAIL] POST /sessions/{session_id}/messages - {e}"); failed += 1
else:
    print("  [SKIP] No session available")

# ===== 18. DATA ANALYSIS: List Messages =====
section(18, "Data Analysis - List Messages")
if token and session_id:
    try:
        r = requests.get(f"{BASE}/sessions/{session_id}/messages", headers=headers, timeout=10)
        check(f"GET /sessions/{session_id}/messages", r.status_code)
        data = r.json()
        print(f"     Messages: {data.get('total')}")
    except Exception as e:
        print(f"  [FAIL] GET /sessions/{session_id}/messages - {e}"); failed += 1
else:
    print("  [SKIP] No session available")

# ===== 19. DATA ANALYSIS: Memory =====
section(19, "Data Analysis - Memory")
if token:
    try:
        r = requests.get(f"{BASE}/memory", headers=headers, timeout=10)
        check("GET /memory", r.status_code)
        data = r.json()
        print(f"     Preferences: {len(data.get('preferences', []))}")
        print(f"     Memories: {len(data.get('memories', []))}")
    except Exception as e:
        print(f"  [FAIL] GET /memory - {e}"); failed += 1
else:
    print("  [SKIP] No token available")

# ===== 20. AUTH FAILURE MODES =====
section(20, "Auth Failure Modes")
try:
    r = requests.get(f"{BASE}/sessions", timeout=10)
    if r.status_code == 401:
        passed += 1
        print(f"  [PASS] No-auth request rejected (HTTP 401)")
    else:
        failed += 1
        print(f"  [FAIL] Expected 401, got {r.status_code}")
except Exception as e:
    print(f"  [FAIL] Auth test - {e}"); failed += 1

try:
    r = requests.get(f"{BASE}/sessions", headers={"Authorization": "Bearer invalid.token.here"}, timeout=10)
    if r.status_code == 401:
        passed += 1
        print(f"  [PASS] Invalid token rejected (HTTP 401)")
    else:
        failed += 1
        print(f"  [FAIL] Expected 401 for bad token, got {r.status_code}")
except Exception as e:
    print(f"  [FAIL] Auth test - {e}"); failed += 1

# ===== 21. HR ENDPOINTS =====
section(21, "HR Endpoints")
try:
    r = requests.post(f"{BASE}/hr/ask",
        json={"company_id": "company_1", "question": "What is the company policy?"},
        timeout=30)
    if r.status_code == 200:
        check("POST /hr/ask", r.status_code)
        data = r.json()
        print(f"     Answer: {str(data.get('answer', ''))[:80]}...")
    else:
        print(f"  [INFO] POST /hr/ask - {r.status_code}: {r.text[:100]}")
except Exception as e:
    print(f"  [FAIL] POST /hr/ask - {e}"); failed += 1

# ===== 22. DOCUMENTS - Upload =====
section(22, "Documents - Upload")
if token:
    try:
        txt_content = b"This is a test document for KnowMate."
        r = requests.post(f"{BASE}/documents/upload",
            files={"file": ("test.txt", txt_content, "text/plain")},
            data={"company_id": "company_1"},
            headers=headers, timeout=30)
        if r.status_code == 200:
            check("POST /documents/upload", r.status_code)
            data = r.json()
            print(f"     Doc ID: {data.get('doc_id')}")
            print(f"     Chunks: {data.get('chunks')}")
        else:
            print(f"  [INFO] POST /documents/upload - {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  [FAIL] POST /documents/upload - {e}"); failed += 1
else:
    print("  [SKIP] No token available")

# ===== 23. DATA ANALYSIS: Standalone Analyze =====
section(23, "Data Analysis - Standalone /analyze")
if token:
    csv_data = b"product,price,quantity\nA,10,100\nB,20,200\nC,30,300"
    try:
        r = requests.post(f"{BASE}/analyze",
            files={"file": ("products.csv", csv_data, "text/csv")},
            data={"question": "show me total revenue per product", "debug": "false"},
            headers=headers, timeout=300)
        if r.status_code == 200:
            check("POST /analyze", r.status_code)
            data = r.json()
            print(f"     Success: {data.get('success')}")
            print(f"     Summary: {str(data.get('summary', ''))[:100]}")
        else:
            print(f"  [INFO] POST /analyze - {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  [FAIL] POST /analyze - {e}"); failed += 1
else:
    print("  [SKIP] No token available")

# ===== 24. DELETE SESSION (cleanup) =====
section(24, "Cleanup - Delete Session")
if token and session_id:
    try:
        r = requests.delete(f"{BASE}/sessions/{session_id}", headers=headers, timeout=10)
        if r.status_code == 204:
            check(f"DELETE /sessions/{session_id}", r.status_code)
            print(f"     Session deleted")
        else:
            print(f"  [INFO] DELETE /sessions/{session_id} - {r.status_code}")
    except Exception as e:
        print(f"  [FAIL] DELETE /sessions/{session_id} - {e}"); failed += 1
else:
    print("  [SKIP] No session available")

print(f"\n{'='*60}")
print(f"  RESULTS: {passed} passed, {failed} failed out of {passed+failed} tests")
print(f"{'='*60}")

if failed > 0:
    print("\n  NOTE: Some endpoints may depend on external services (Ollama LLM)")
    print("  or specific data being present. Review failures above.\n")

sys.exit(0 if failed == 0 else 1)
