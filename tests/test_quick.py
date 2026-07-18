"""Complete app test — agents, session isolation, unknown answers, CRUD."""
import requests, os

BASE = "http://localhost:8000"
WORK = r"C:\Users\DELL\Desktop\111\11\Depi\KnowMate"
PASS = 0
FAIL = 0

def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {label}" + (f" -- {detail}" if detail else ""))
    else:
        FAIL += 1
        print(f"  [FAIL] {label}" + (f" -- {detail}" if detail else ""))

# --- Auth ---
r = requests.post(f"{BASE}/auth/login", data={"username":"testadmin_fullapp@testcorp.com","password":"TestPass123!"}, timeout=10)
check("Login", r.status_code == 200, f"status={r.status_code}")
token = r.json()["access_token"]
H = {"Authorization": f"Bearer {token}"}
r = requests.get(f"{BASE}/auth/me", headers=H, timeout=5)
cid = str(r.json().get("company_id", 1))
check("Get user/me", r.status_code == 200)

# --- Upload ---
print("\n--- Document Upload ---")
tp = os.path.join(WORK, "TestData", "policy.txt")
with open(tp, "rb") as f:
    r = requests.post(f"{BASE}/documents/upload", headers=H,
                       files={"file": ("policy.txt", f, "text/plain")},
                       data={"company_id": cid}, timeout=30)
check("Upload document", r.status_code == 200, f"status={r.status_code}")
doc_id = r.json().get("doc_id") if r.status_code == 200 else None
check("Upload returns doc_id", doc_id is not None)

# --- Agents ---
print("\n--- Agent Tests ---")
for label, agent_type, question in [
    ("HR agent", "hr", "What is the vacation policy?"),
    ("HR unknown", "hr", "What is the company's stock ticker?"),
    ("General agent", "default", "What is KnowMate?"),
    ("General unknown", "default", "How do I fix my car?"),
    ("Marketing agent", "marketing", "How to increase brand awareness?"),
    ("Marketing unknown", "marketing", "What is quantum computing?"),
]:
    r = requests.post(f"{BASE}/sessions", headers=H, json={"title": label}, timeout=10)
    sid = r.json()["id"]
    r = requests.post(f"{BASE}/api/chat", headers=H, json={
        "question": question, "company_id": cid, "agent_type": agent_type,
        "session_id": sid, "files": []
    }, timeout=120)
    check(f"{label}: status 200", r.status_code == 200, f"status={r.status_code}")
    if r.status_code == 200:
        ans = r.json()["answer"]
        has_disclaimer = any(phrase in ans.lower() for phrase in ["couldn't find", "don't have", "not available", "not mentioned", "not found"])
        check(f"{label}: has unknown disclaimer", has_disclaimer, f"answer starts: {ans[:80]}...")
        check(f"{label}: has non-empty answer", len(ans) > 20)
    requests.delete(f"{BASE}/sessions/{sid}", headers=H, timeout=10)

# --- Session Isolation ---
print("\n--- Session Isolation ---")
r = requests.post(f"{BASE}/sessions", headers=H, json={"title":"Iso A"}, timeout=10)
sid_a = r.json()["id"]
r = requests.post(f"{BASE}/sessions", headers=H, json={"title":"Iso B"}, timeout=10)
sid_b = r.json()["id"]
check("Sessions have different IDs", sid_a != sid_b)

# Session A: ask with file attached
r = requests.post(f"{BASE}/api/chat", headers=H, json={
    "question":"What is the vacation policy?", "company_id": cid,
    "agent_type":"default", "session_id": sid_a, "files":["policy.txt"]
}, timeout=120)
a_ans = r.json()["answer"] if r.status_code == 200 else ""
a_srcs = r.json().get("sources", []) if r.status_code == 200 else []

# Session B: ask without file attached
r = requests.post(f"{BASE}/api/chat", headers=H, json={
    "question":"What is the vacation policy?", "company_id": cid,
    "agent_type":"default", "session_id": sid_b, "files":[]
}, timeout=120)
b_ans = r.json()["answer"] if r.status_code == 200 else ""
b_srcs = r.json().get("sources", []) if r.status_code == 200 else []

check("Session A got response", len(a_ans) > 0)
check("Session B got response", len(b_ans) > 0)
requests.delete(f"{BASE}/sessions/{sid_a}", headers=H, timeout=10)
requests.delete(f"{BASE}/sessions/{sid_b}", headers=H, timeout=10)

# --- Sessions CRUD ---
print("\n--- Sessions CRUD ---")
r = requests.post(f"{BASE}/sessions", headers=H, json={"title":"CRUD Test"}, timeout=10)
crud_sid = r.json()["id"]
check("Create session", r.status_code == 201, f"status={r.status_code}")

r = requests.get(f"{BASE}/sessions", headers=H, timeout=10)
check("List sessions", r.status_code == 200)
if r.status_code == 200:
    items = r.json().get("items", [])
    check("List sessions has items", len(items) > 0, f"count={len(items)}")

r = requests.delete(f"{BASE}/sessions/{crud_sid}", headers=H, timeout=10)
check("Delete session", r.status_code in (200, 204), f"status={r.status_code}")

# --- Document Delete ---
print("\n--- Document Delete ---")
if doc_id:
    r = requests.delete(f"{BASE}/documents/{doc_id}", headers=H, timeout=10)
    check("Delete document", r.status_code == 200, f"status={r.status_code}")

# --- Summary ---
print(f"\n{'='*50}")
print(f"RESULTS: {PASS} passed, {FAIL} failed, {PASS+FAIL} total")
print(f"{'='*50}")
