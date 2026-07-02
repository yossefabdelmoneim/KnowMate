import httpx

c = httpx.Client(base_url='http://localhost:8000', timeout=120)

r = c.post('/auth/login', data={'username': 'ragtest@example.com', 'password': 'Test1234!'})
t = r.json()['access_token']
print(f'Login: OK')

for agent in ['general', 'hr', 'marketing']:
    r = c.post('/api/chat', json={'question':'What was decided about AI in the meeting?','company_id':'1','agent_type':agent}, headers={'Authorization':f'Bearer {t}'})
    body = r.json()
    ans = body.get('answer','?')[:80]
    print(f'[{agent}] {r.status_code} {ans}')
