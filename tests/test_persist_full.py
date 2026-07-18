import httpx, json

c = httpx.Client(base_url='http://localhost:8000', timeout=120)

# Register fresh user
r = c.post('/auth/register', json={'email': 'persist@test.com', 'password': 'Pass1234!', 'full_name': 'Persist Test', 'role': 'admin'})
print(f'Register: {r.status_code}')

r = c.post('/auth/login', data={'username': 'persist@test.com', 'password': 'Pass1234!'})
t = r.json()['access_token']
print(f'Login: OK')

# 1. Send first message (no session_id)
r = c.post('/api/chat', json={'question': 'What is AI?', 'company_id': '1', 'agent_type': 'general', 'session_id': None}, headers={'Authorization': f'Bearer {t}'})
body = r.json()
sid = body.get('session_id', '')
print(f'Chat 1: session_id={sid}')

# 2. Send second message (with session_id)
r = c.post('/api/chat', json={'question': 'Tell me more', 'company_id': '1', 'agent_type': 'general', 'session_id': sid}, headers={'Authorization': f'Bearer {t}'})
print(f'Chat 2: {r.status_code}')

# 3. List sessions
r = c.get('/sessions', headers={'Authorization': f'Bearer {t}'})
data = r.json()
print(f'\nSessions: {len(data["items"])}')
for s in data['items']:
    print(f'  id={s["id"][:8]} title="{s["title"]}" msgs={s["message_count"]}')

# 4. Get messages
r = c.get(f'/sessions/{sid}/messages', headers={'Authorization': f'Bearer {t}'})
data = r.json()
print(f'\nMessages: {len(data["items"])}')
for m in data['items']:
    print(f'  [{m["role"]}] seq={m["seq"]} "{m["content"][:50]}"')

# 5. Simulate logout/login
r = c.post('/auth/login', data={'username': 'persist@test.com', 'password': 'Pass1234!'})
t2 = r.json()['access_token']
print(f'\nAfter re-login:')

r = c.get('/sessions', headers={'Authorization': f'Bearer {t2}'})
data = r.json()
print(f'Sessions: {len(data["items"])}')
for s in data['items']:
    print(f'  id={s["id"][:8]} title="{s["title"]}" msgs={s["message_count"]}')

r = c.get(f'/sessions/{sid}/messages', headers={'Authorization': f'Bearer {t2}'})
data = r.json()
print(f'Messages: {len(data["items"])}')
