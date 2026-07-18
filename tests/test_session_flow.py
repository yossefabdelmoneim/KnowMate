import httpx, json

c = httpx.Client(base_url='http://localhost:8000')

# 1. Register
r = c.post('/auth/register', json={'email': 'sessionflow@test.com', 'password': 'Pass1234!', 'full_name': 'Session Tester', 'role': 'admin'})
print(f'Register: {r.status_code}')

# 2. Login
r = c.post('/auth/login', data={'username': 'sessionflow@test.com', 'password': 'Pass1234!'})
t = r.json()['access_token']
print(f'Login: OK, token saved')

# 3. Send a chat message (creates session)
r = c.post('/api/chat', json={'question': 'What is AI?', 'company_id': '1', 'agent_type': 'default', 'session_id': None}, headers={'Authorization': f'Bearer {t}'})
body = r.json()
sid = body.get('session_id', '')
print(f'Chat: status={r.status_code}, session_id={sid}')

# 4. Send another message in same session
r = c.post('/api/chat', json={'question': 'Tell me more', 'company_id': '1', 'agent_type': 'default', 'session_id': sid}, headers={'Authorization': f'Bearer {t}'})
print(f'Chat2: status={r.status_code}')

# 5. List sessions
r = c.get('/sessions', headers={'Authorization': f'Bearer {t}'})
data = r.json()
print(f'Sessions before logout: {len(data["items"])}')

# 6. Simulate sign out and sign back in
r = c.post('/auth/login', data={'username': 'sessionflow@test.com', 'password': 'Pass1234!'})
t2 = r.json()['access_token']
print(f'\n=== After re-login ===')

# 7. List sessions after re-login
r = c.get('/sessions', headers={'Authorization': f'Bearer {t2}'})
data = r.json()
print(f'Sessions after re-login: {len(data["items"])}')
for s in data['items']:
    print(f'  title="{s["title"]}" msgs={s["message_count"]}')

# 8. Get messages for the session
r = c.get(f'/sessions/{sid}/messages', headers={'Authorization': f'Bearer {t2}'})
data = r.json()
print(f'Messages in session: {len(data["items"])}')
for m in data['items']:
    print(f'  [{m["role"]}] {m["content"][:60]}')

print('\n=== ALL GOOD ===')
