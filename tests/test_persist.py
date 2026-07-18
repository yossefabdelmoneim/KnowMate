import httpx, traceback

c = httpx.Client(base_url='http://localhost:8000')

# Register a fresh user
r = c.post('/auth/register', json={'email': 'test@persist.com', 'password': 'Test123!@#', 'full_name': 'Test', 'role': 'admin'})
print(f'Register: {r.status_code}')

# Login
r = c.post('/auth/login', data={'username': 'test@persist.com', 'password': 'Test123!@#'})
t = r.json()['access_token']
print(f'Login: {r.status_code}, token: {t[:20]}...')

# Send first message (no session_id — creates session automatically)
r = c.post('/api/chat', json={'question': 'hi', 'company_id': '1', 'agent_type': 'default'}, headers={'Authorization': f'Bearer {t}'})
print(f'Chat 1: {r.status_code}, answer: {r.json()["answer"][:60]}')
sid1 = r.json().get('session_id', '')
print(f'  session_id: {sid1}')

# Send second message (with session_id — persists to same session)
r = c.post('/api/chat', json={'question': 'hello', 'company_id': '1', 'agent_type': 'default', 'session_id': sid1}, headers={'Authorization': f'Bearer {t}'})
print(f'Chat 2: {r.status_code}, answer: {r.json()["answer"][:60]}')
sid2 = r.json().get('session_id', '')
print(f'  session_id: {sid2}')

# List sessions — should show at least 1
try:
    r = c.get('/sessions', headers={'Authorization': f'Bearer {t}'})
    print(f'\nList sessions: {r.status_code} body_len={len(r.content)} raw={r.text[:300]}')
    if r.status_code == 200 and r.content:
        sessions_body = r.json()
        sessions = sessions_body.get('items', [])
        print(f'Sessions: {len(sessions)}')
except Exception as e:
    traceback.print_exc()
for s in sessions:
    print(f'  {s["id"][:8]}... - {s["title"][:40]} ({s.get("message_count",0)} msgs)')

# Get messages for session
r = c.get(f'/sessions/{sid1}/messages', headers={'Authorization': f'Bearer {t}'})
msgs = r.json().get('items', [])
print(f'\nMessages in session: {len(msgs)}')
for m in msgs:
    print(f'  [{m["role"]}] {m["content"][:50]}')
