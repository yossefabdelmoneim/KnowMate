"""Test data analysis routes with proper UUID-based token."""
import requests
import sys
import uuid
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlOTg3ZjE4YS03MTMyLTQxMDEtODI0OS0xZTE0ZDlmNGE3NGQiLCJpYXQiOjE3ODMwMTA3MDgsImV4cCI6MTc4MzAxNDMwOCwidHlwZSI6ImFjY2VzcyJ9.17v6kbqXfmkBQ3ihOSFQSRtbm_lx-_hsjbx-9bx0pGs"
H = {"Authorization": f"Bearer {TOKEN}"}

def ok(name, status):
    ok = 200 <= status < 300
    print(f"  [{'PASS' if ok else 'FAIL'}] {name} (HTTP {status})")
    return ok

print("=" * 60)
print("  DATA ANALYSIS ROUTES TEST")
print("=" * 60)

# 1. Supported types
r = requests.get(f"{BASE}/sessions/_meta/supported-types", timeout=10)
ok("GET /sessions/_meta/supported-types", r.status_code)
print(f"     Extensions: {r.json().get('extensions')}")

# 2. Create session
r = requests.post(f"{BASE}/sessions", json={"title": "Test", "description": "Test session"}, headers=H, timeout=10)
ok("POST /sessions", r.status_code)
sid = r.json().get("id") if r.status_code == 201 else None
if sid:
    print(f"     Session ID: {sid}")
else:
    print(f"     Error: {r.text[:100]}")

# 3. List sessions
r = requests.get(f"{BASE}/sessions", headers=H, timeout=10)
ok("GET /sessions", r.status_code)
total = r.json().get("total", 0) if r.status_code == 200 else 0
print(f"     Total: {total}")

# 4. Get session
if sid:
    r = requests.get(f"{BASE}/sessions/{sid}", headers=H, timeout=10)
    ok(f"GET /sessions/{sid}", r.status_code)
    if r.status_code == 200:
        print(f"     Title: {r.json().get('title')}")

# 5. Update session
if sid:
    r = requests.patch(f"{BASE}/sessions/{sid}", json={"title": "Updated Test"}, headers=H, timeout=10)
    ok(f"PATCH /sessions/{sid}", r.status_code)
    if r.status_code == 200:
        print(f"     Updated: {r.json().get('title')}")

# 6. Upload dataset
if sid:
    csv = b"city,revenue,population\nCairo,1200000,10000000\nGiza,620000,4000000\nAlex,310000,1500000"
    r = requests.post(f"{BASE}/sessions/{sid}/dataset", files={"file": ("cities.csv", csv, "text/csv")}, headers=H, timeout=15)
    ok(f"POST /sessions/{sid}/dataset", r.status_code)
    if r.status_code == 201:
        ds = r.json().get("dataset", {})
        print(f"     File: {ds.get('original_filename')} ({ds.get('row_count')} rows)")
    else:
        print(f"     {r.text[:100]}")

# 7. Send message
if sid:
    r = requests.post(f"{BASE}/sessions/{sid}/messages", json={"question": "show me top 3 cities by revenue", "debug": True}, headers=H, timeout=300)
    ok(f"POST /sessions/{sid}/messages", r.status_code)
    if r.status_code == 200:
        print(f"     Success: {r.json().get('success')}")
        print(f"     Summary: {str(r.json().get('summary', ''))[:80]}")
    else:
        print(f"     {r.text[:100]}")

# 8. List messages
if sid:
    r = requests.get(f"{BASE}/sessions/{sid}/messages", headers=H, timeout=10)
    ok(f"GET /sessions/{sid}/messages", r.status_code)
    print(f"     Messages: {r.json().get('total')}")

# 9. Memory
r = requests.get(f"{BASE}/memory", headers=H, timeout=10)
ok("GET /memory", r.status_code)
data = r.json()
print(f"     Preferences: {len(data.get('preferences', []))}, Memories: {len(data.get('memories', []))}")

# 10. /analyze standalone
csv = b"product,price,qty\nA,10,100\nB,20,200\nC,30,300"
r = requests.post(f"{BASE}/analyze", files={"file": ("products.csv", csv, "text/csv")}, data={"question": "total revenue", "debug": "false"}, headers=H, timeout=300)
ok("POST /analyze", r.status_code)
if r.status_code == 200:
    print(f"     Success: {r.json().get('success')}")
    print(f"     Summary: {str(r.json().get('summary', ''))[:80]}")
else:
    print(f"     {r.text[:100]}")

# 11. Cleanup - delete session
if sid:
    r = requests.delete(f"{BASE}/sessions/{sid}", headers=H, timeout=10)
    ok(f"DELETE /sessions/{sid}", r.status_code)
    print(f"     Deleted")

print(f"\n{'='*60}")
print("  DATA ANALYSIS TEST COMPLETE")
print(f"{'='*60}")
