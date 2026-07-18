import subprocess, time, sys, os, requests, traceback

os.chdir(r"C:\Users\DELL\Desktop\111\11\Depi\KnowMate")

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.Back_End.main:app", "--host", "0.0.0.0", "--port", "8000"],
    stderr=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)

time.sleep(12)

try:
    r = requests.post("http://localhost:8000/auth/login", data={"username": "testadmin_fullapp@testcorp.com", "password": "TestPass123!"}, timeout=10)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test chat - use longer timeout and check response
    try:
        r = requests.post("http://localhost:8000/api/chat", json={
            "question": "Hello!",
            "company_id": "1",
            "agent_type": "hr",
            "files": []
        }, headers=headers, timeout=120)
        print(f"Chat Status: {r.status_code}")
        print(f"Chat Response: {r.text[:1000]}")
    except requests.exceptions.Timeout:
        print("Chat request timed out after 120s")
    except Exception as e:
        print(f"Chat error: {e}")

    # Read all available stdout/stderr
    time.sleep(2)
    
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

proc.terminate()
proc.wait(timeout=5)
try:
    stderr = proc.stderr.read()
    stdout = proc.stdout.read()
    if stderr:
        print("\n--- STDERR (last 5000 chars) ---")
        print(stderr[-5000:])
    if stdout:
        print("\n--- STDOUT (last 5000 chars) ---")
        print(stdout[-5000:])
except:
    pass
