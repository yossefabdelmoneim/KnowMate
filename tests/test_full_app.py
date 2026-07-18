"""Full app test script — tests backend API endpoints, agents, and session isolation."""

import requests
import json
import time
import sys
import os

BASE = "http://localhost:8000"
RESULTS = []

def test(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    RESULTS.append((name, passed))
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ──────────────────────────────────────────────────────────────────
# 1. Health & Root
# ──────────────────────────────────────────────────────────────────
section("1. Health & Root Endpoints")

try:
    r = requests.get(f"{BASE}/", timeout=5)
    test("GET / returns 200", r.status_code == 200)
    data = r.json()
    test("GET / returns service name", data.get("service") == "KnowMate")
except Exception as e:
    test("GET / root endpoint", False, str(e))

# ──────────────────────────────────────────────────────────────────
# 2. Auth Flow
# ──────────────────────────────────────────────────────────────────
section("2. Auth Flow")

# Register a test company
try:
    r = requests.post(f"{BASE}/companies/register", json={
        "company_name": "TestCorp_FullApp",
        "admin": {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin_fullapp@testcorp.com",
            "password": "TestPass123!"
        }
    }, timeout=10)
    reg_ok = r.status_code in (200, 201, 409)  # 409 = already exists
    test("POST /companies/register", reg_ok, f"status={r.status_code}")
except Exception as e:
    test("POST /companies/register", False, str(e))

# Login
token = None
try:
    r = requests.post(f"{BASE}/auth/login", data={
        "username": "testadmin_fullapp@testcorp.com",
        "password": "TestPass123!"
    }, timeout=10)
    test("POST /auth/login returns 200", r.status_code == 200, f"status={r.status_code}")
    data = r.json()
    token = data.get("access_token")
    test("Login returns access_token", token is not None)
except Exception as e:
    test("POST /auth/login", False, str(e))

headers = {"Authorization": f"Bearer {token}"} if token else {}

# Get current user
try:
    r = requests.get(f"{BASE}/auth/me", headers=headers, timeout=5)
    test("GET /auth/me returns 200", r.status_code == 200, f"status={r.status_code}")
    user = r.json()
    test("GET /auth/me returns user data", "email" in user, f"email={user.get('email')}")
    company_id = str(user.get("company_id", 1))
except Exception as e:
    test("GET /auth/me", False, str(e))
    company_id = "1"

# ──────────────────────────────────────────────────────────────────
# 3. Document Upload
# ──────────────────────────────────────────────────────────────────
section("3. Document Upload")

# Upload a test file
test_file_path = os.path.join(os.path.dirname(__file__), "..", "TestData", "policy.txt")
if not os.path.exists(test_file_path):
    test_file_path = os.path.join(os.path.dirname(__file__), "..", "TestData", "sales.csv")

doc_id = None
try:
    with open(test_file_path, "rb") as f:
        files = {"file": (os.path.basename(test_file_path), f)}
        data = {"company_id": company_id}
        r = requests.post(f"{BASE}/documents/upload", files=files, data=data, headers=headers, timeout=30)
    test("POST /documents/upload returns 200", r.status_code == 200, f"status={r.status_code}")
    resp = r.json()
    doc_id = resp.get("doc_id")
    test("Upload returns doc_id", doc_id is not None, f"doc_id={doc_id}")
    test("Upload returns chunks > 0", resp.get("chunks", 0) > 0, f"chunks={resp.get('chunks')}")
except Exception as e:
    test("POST /documents/upload", False, str(e))

# ──────────────────────────────────────────────────────────────────
# 4. HR Agent
# ──────────────────────────────────────────────────────────────────
section("4. HR Agent")

# Test 4a: HR query about a document topic
try:
    r = requests.post(f"{BASE}/api/chat", json={
        "question": "What is the company's return policy?",
        "company_id": company_id,
        "agent_type": "hr",
        "files": [os.path.basename(test_file_path)]
    }, headers=headers, timeout=120)
    test("HR agent: returns 200", r.status_code == 200, f"status={r.status_code}")
    data = r.json()
    test("HR agent: returns answer", bool(data.get("answer")), f"answer_len={len(data.get('answer', ''))}")
    test("HR agent: returns session_id", bool(data.get("session_id")))
    hr_session_id = data.get("session_id")
except Exception as e:
    test("HR agent: query", False, str(e))
    hr_session_id = None

# Test 4b: HR agent when answer is NOT in documents (should say unknown + general knowledge)
try:
    r = requests.post(f"{BASE}/api/chat", json={
        "question": "What is the company's stock price?",
        "company_id": company_id,
        "agent_type": "hr",
    }, headers=headers, timeout=120)
    test("HR agent (unknown): returns 200", r.status_code == 200)
    data = r.json()
    answer = data.get("answer", "")
    test("HR agent (unknown): provides answer", bool(answer), f"answer_len={len(answer)}")
    has_unknown = "couldn't find" in answer.lower() or "not available" in answer.lower() or "not found" in answer.lower() or "general" in answer.lower()
    test("HR agent (unknown): admits not found + provides general info", has_unknown, f"answer_preview={answer[:200]}")
except Exception as e:
    test("HR agent (unknown): query", False, str(e))

# Test 4c: HR general chat (greeting)
try:
    r = requests.post(f"{BASE}/api/chat", json={
        "question": "Hello!",
        "company_id": company_id,
        "agent_type": "hr",
    }, headers=headers, timeout=120)
    test("HR agent (greeting): returns 200", r.status_code == 200)
    data = r.json()
    test("HR agent (greeting): provides greeting response", bool(data.get("answer")), f"answer_len={len(data.get('answer', ''))}")
except Exception as e:
    test("HR agent (greeting): query", False, str(e))

# ──────────────────────────────────────────────────────────────────
# 5. Marketing Agent
# ──────────────────────────────────────────────────────────────────
section("5. Marketing Agent")

# Test 5a: Marketing query with docs
try:
    r = requests.post(f"{BASE}/api/chat", json={
        "question": "Write a marketing email about our return policy",
        "company_id": company_id,
        "agent_type": "marketing",
        "files": [os.path.basename(test_file_path)]
    }, headers=headers, timeout=120)
    test("Marketing agent: returns 200", r.status_code == 200, f"status={r.status_code}")
    data = r.json()
    test("Marketing agent: returns answer", bool(data.get("answer")), f"answer_len={len(data.get('answer', ''))}")
except Exception as e:
    test("Marketing agent: query", False, str(e))

# Test 5b: Marketing agent when answer is NOT in documents
try:
    r = requests.post(f"{BASE}/api/chat", json={
        "question": "What are our Q4 revenue numbers?",
        "company_id": company_id,
        "agent_type": "marketing",
    }, headers=headers, timeout=120)
    test("Marketing agent (unknown): returns 200", r.status_code == 200)
    data = r.json()
    answer = data.get("answer", "")
    test("Marketing agent (unknown): provides answer", bool(answer), f"answer_len={len(answer)}")
    has_fallback = "couldn't find" in answer.lower() or "not available" in answer.lower() or "general" in answer.lower() or "marketing guidance" in answer.lower()
    test("Marketing agent (unknown): admits not found + provides general guidance", has_fallback, f"answer_preview={answer[:200]}")
except Exception as e:
    test("Marketing agent (unknown): query", False, str(e))

# ──────────────────────────────────────────────────────────────────
# 6. General/RAG Agent
# ──────────────────────────────────────────────────────────────────
section("6. General/RAG Agent")

# Test 6a: General query with docs
try:
    r = requests.post(f"{BASE}/api/chat", json={
        "question": "Summarize this document",
        "company_id": company_id,
        "agent_type": "general",
        "files": [os.path.basename(test_file_path)]
    }, headers=headers, timeout=120)
    test("General agent: returns 200", r.status_code == 200, f"status={r.status_code}")
    data = r.json()
    test("General agent: returns answer", bool(data.get("answer")), f"answer_len={len(data.get('answer', ''))}")
except Exception as e:
    test("General agent: query", False, str(e))

# Test 6b: General agent when no documents / unknown answer
try:
    r = requests.post(f"{BASE}/api/chat", json={
        "question": "What is quantum computing?",
        "company_id": company_id,
        "agent_type": "general",
    }, headers=headers, timeout=120)
    test("General agent (unknown): returns 200", r.status_code == 200)
    data = r.json()
    answer = data.get("answer", "")
    test("General agent (unknown): provides answer", bool(answer), f"answer_len={len(answer)}")
    has_fallback = "couldn't find" in answer.lower() or "not found" in answer.lower() or "general information" in answer.lower() or "quantum" in answer.lower()
    test("General agent (unknown): admits not found or answers with general knowledge", has_fallback, f"answer_preview={answer[:200]}")
except Exception as e:
    test("General agent (unknown): query", False, str(e))

# ──────────────────────────────────────────────────────────────────
# 7. Session Isolation
# ──────────────────────────────────────────────────────────────────
section("7. Session Isolation — Files Don't Carry Over")

session_a_id = None
session_b_id = None

# Session A: upload file and chat
try:
    r = requests.post(f"{BASE}/api/chat", json={
        "question": "What does this document say?",
        "company_id": company_id,
        "agent_type": "general",
        "files": [os.path.basename(test_file_path)],
    }, headers=headers, timeout=120)
    test("Session A: chat with file succeeds", r.status_code == 200)
    data = r.json()
    session_a_id = data.get("session_id")
    test("Session A: has session_id", session_a_id is not None)
except Exception as e:
    test("Session A: chat with file", False, str(e))

# Session B: new chat WITHOUT any files
try:
    r = requests.post(f"{BASE}/api/chat", json={
        "question": "What is the weather today?",
        "company_id": company_id,
        "agent_type": "general",
        "files": [],
    }, headers=headers, timeout=120)
    test("Session B: chat without files succeeds", r.status_code == 200)
    data = r.json()
    session_b_id = data.get("session_id")
    test("Session B: has different session_id", session_b_id is not None and session_b_id != session_a_id, f"a={session_a_id}, b={session_b_id}")
except Exception as e:
    test("Session B: chat without files", False, str(e))

# Verify sessions are independent
if session_a_id and session_b_id:
    try:
        r_a = requests.get(f"{BASE}/sessions/{session_a_id}/messages", headers=headers, timeout=10)
        r_b = requests.get(f"{BASE}/sessions/{session_b_id}/messages", headers=headers, timeout=10)
        test("Sessions exist independently", r_a.status_code == 200 and r_b.status_code == 200)
    except Exception as e:
        test("Sessions independence check", False, str(e))

# ──────────────────────────────────────────────────────────────────
# 8. Sessions List
# ──────────────────────────────────────────────────────────────────
section("8. Sessions List")

try:
    r = requests.get(f"{BASE}/sessions", headers=headers, timeout=10)
    test("GET /sessions returns 200", r.status_code == 200)
    data = r.json()
    items = data.get("items", [])
    test("GET /sessions returns items", len(items) > 0, f"count={len(items)}")
    session_ids = [s["id"] for s in items]
    if session_a_id:
        test("Session A appears in list", session_a_id in session_ids)
    if session_b_id:
        test("Session B appears in list", session_b_id in session_ids)
except Exception as e:
    test("GET /sessions", False, str(e))

# ──────────────────────────────────────────────────────────────────
# 9. Delete Session
# ──────────────────────────────────────────────────────────────────
section("9. Delete Session")

if session_b_id:
    try:
        r = requests.delete(f"{BASE}/sessions/{session_b_id}", headers=headers, timeout=10)
        test("DELETE /sessions/{id} returns 204", r.status_code == 204, f"status={r.status_code}")

        r2 = requests.get(f"{BASE}/sessions", headers=headers, timeout=10)
        remaining_ids = [s["id"] for s in r2.json().get("items", [])]
        test("Deleted session no longer in list", session_b_id not in remaining_ids)
    except Exception as e:
        test("DELETE session", False, str(e))

# ──────────────────────────────────────────────────────────────────
# 10. Document Delete
# ──────────────────────────────────────────────────────────────────
section("10. Document Delete")

if doc_id:
    try:
        r = requests.delete(f"{BASE}/documents/{doc_id}?company_id={company_id}", headers=headers, timeout=10)
        test("DELETE /documents/{doc_id} returns 200", r.status_code == 200, f"status={r.status_code}")
    except Exception as e:
        test("DELETE document", False, str(e))

# ──────────────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────────────
section("TEST SUMMARY")
total = len(RESULTS)
passed = sum(1 for _, p in RESULTS if p)
failed = total - passed
print(f"\n  Total: {total}  |  Passed: {passed}  |  Failed: {failed}")
if failed:
    print("\n  Failed tests:")
    for name, p in RESULTS:
        if not p:
            print(f"    - {name}")
else:
    print("\n  All tests passed!")

sys.exit(0 if failed == 0 else 1)
