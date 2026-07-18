import httpx, json, os

c = httpx.Client(base_url='http://localhost:8000')

# Fresh user
r = c.post('/auth/register', json={'email': 'ragtest@example.com', 'password': 'Test1234!', 'full_name': 'Rag Tester', 'role': 'admin'})
print(f'Register: {r.status_code}')

r = c.post('/auth/login', data={'username': 'ragtest@example.com', 'password': 'Test1234!'})
t = r.json()['access_token']
print(f'Login: OK')

# Create a test file
os.makedirs('test_data', exist_ok=True)
with open('test_data/meeting.txt', 'w') as f:
    f.write("""
Meeting Notes: Q3 Planning Session
Date: June 15, 2026
Attendees: Alice, Bob, Charlie, Diana

Key Decisions:
1. Launch new AI-powered search feature by September 2026
2. Increase engineering team by 5 new hires
3. Budget allocation: $500K for AI development, $200K for marketing
4. Customer satisfaction target: 92% by year end

Action Items:
- Alice: Finalize AI model selection by July 1
- Bob: Draft job descriptions for 5 new engineering positions
- Charlie: Prepare marketing budget breakdown
- Diana: Set up customer satisfaction tracking dashboard

Next meeting: July 5, 2026
""")

# Upload the document
with open('test_data/meeting.txt', 'rb') as f:
    r = c.post('/documents/upload', data={'company_id': '1'}, files={'file': ('meeting.txt', f, 'text/plain')}, headers={'Authorization': f'Bearer {t}'})
print(f'Upload: {r.status_code}')
print(json.dumps(r.json(), indent=2))

# Ask about the document
r = c.post('/api/chat', json={'question': 'What was decided about AI in the meeting?', 'company_id': '1', 'agent_type': 'default'}, headers={'Authorization': f'Bearer {t}'})
body = r.json()
print(f'\nChat: {r.status_code}')
print(f'Answer: {body["answer"]}')
print(f'Sources: {body["sources"]}')
