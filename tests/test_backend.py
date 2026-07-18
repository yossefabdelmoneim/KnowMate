import httpx
import pytest
import os
import time

# --- Configuration ---
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "securepassword"
TEST_COMPANY_ID = "company_alpha"
TEST_POLICY_FILE_PATH = os.path.join("test_data", "policy.txt")
TEST_SALES_FILE_PATH = os.path.join("test_data", "sales.csv")

# --- Global variables to store state between tests ---
access_token = None
doc_id = None

@pytest.fixture(scope="module")
def client():
    """
    Fixture to provide an httpx client for making requests to the FastAPI app.
    The client is yielded once for the entire test module.
    """
    # Increased timeout to 60 seconds for potentially long-running LLM calls
    with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:
        yield client

@pytest.fixture(scope="module", autouse=True)
def setup_test_data():
    """
    Ensures test data files exist before tests run.
    """
    # Create test_data directory if it doesn't exist
    os.makedirs("test_data", exist_ok=True)

    # Create policy.txt
    with open(TEST_POLICY_FILE_PATH, "w") as f:
        f.write("""# Company Return Policy

Our company offers a comprehensive return policy to ensure customer satisfaction.

**Eligibility:**
- Items must be returned within **30 days** of the purchase date.
- Products must be in their original condition, unused, and with all tags and packaging intact.
- Proof of purchase (receipt or order confirmation) is required for all returns.

**Non-Returnable Items:**
- Perishable goods (e.g., food, flowers)
- Customized or personalized items
- Digital downloads
- Gift cards

**Process:**
1. Contact customer service to initiate a return and receive a Return Merchandise Authorization (RMA) number.
2. Package the item securely, including the RMA number on the outside of the package.
3. Ship the item to the address provided by customer service.

**Refunds:**
- Refunds will be processed within 5-7 business days after the returned item is received and inspected.
- Original shipping charges are non-refundable.
- Refunds will be issued to the original payment method.

For any questions, please contact our support team at support@example.com.
""")

    # Create sales.csv
    with open(TEST_SALES_FILE_PATH, "w") as f:
        f.write("""Date,Product,Category,Sales,UnitsSold,Region
2023-01-01,Laptop,Electronics,1200,1,North
2023-01-01,Mouse,Electronics,25,2,North
2023-01-02,Keyboard,Electronics,75,1,South
2023-01-02,Monitor,Electronics,300,1,East
2023-01-03,Desk,Furniture,150,1,North
2023-01-03,Chair,Furniture,80,1,West
2023-01-04,Laptop,Electronics,1500,1,South
2023-01-04,Webcam,Electronics,50,1,East
2023-01-05,Desk,Furniture,180,1,West
2023-01-05,Mouse,Electronics,30,2,North
""")
    yield
    # Teardown: Clean up test_data directory if needed
    # import shutil
    # shutil.rmtree("test_data", ignore_errors=True)


def test_01_health_check(client: httpx.Client):
    """Test the /health endpoint to ensure the API is running and LLM is available."""
    print("\n--- Test 01: Health Check ---")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["llm_available"] is True
    print(f"Health check successful: {data}")

def test_02_register_user(client: httpx.Client):
    """Test user registration."""
    print("\n--- Test 02: Register User ---")
    response = client.post(
        "/auth/register",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": "Test User",
            "role": "admin", # Register as admin for full test coverage
            "company_id": None
        },
    )
    # Expect 201 if created, or 400 if already registered (from previous test run)
    assert response.status_code in [201, 400]
    if response.status_code == 201:
        data = response.json()
        assert data["email"] == TEST_USER_EMAIL
        print(f"User registered: {data['email']}")
    else:
        print(f"User already registered: {TEST_USER_EMAIL}")


def test_03_login_user(client: httpx.Client):
    """Test user login and retrieve access token."""
    print("\n--- Test 03: Login User ---")
    global access_token
    response = client.post(
        "/auth/login",
        data={
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    access_token = data["access_token"]
    print(f"User logged in, token obtained: {access_token[:10]}...")


def test_04_get_current_user(client: httpx.Client):
    """Test retrieving current user profile with the access token."""
    print("\n--- Test 04: Get Current User ---")
    assert access_token is not None, "Access token not obtained from login test."
    response = client.get(
        "/auth/me", # Updated path to /auth/me
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_USER_EMAIL
    print(f"Current user profile: {data['email']}")


def test_05_upload_document(client: httpx.Client):
    """Test uploading a document for RAG."""
    print("\n--- Test 05: Upload Document ---")
    global doc_id
    assert access_token is not None, "Access token not obtained from login test."
    assert os.path.exists(TEST_POLICY_FILE_PATH), f"Test file not found: {TEST_POLICY_FILE_PATH}"

    with open(TEST_POLICY_FILE_PATH, "rb") as f:
        response = client.post(
            "/documents/upload",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": (os.path.basename(TEST_POLICY_FILE_PATH), f, "text/plain")},
            data={"company_id": TEST_COMPANY_ID}
        )
    assert response.status_code == 200
    data = response.json()
    assert "doc_id" in data
    assert data["chunks"] > 0
    doc_id = data["doc_id"]
    print(f"Document uploaded, doc_id: {doc_id}, chunks: {data['chunks']}")
    time.sleep(2) # Give ChromaDB a moment to process


def test_06_search_documents(client: httpx.Client):
    """Test searching for documents."""
    print("\n--- Test 06: Search Documents ---")
    assert access_token is not None, "Access token not obtained from login test."
    response = client.post(
        "/search/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "query": "What is the return policy?",
            "company_id": TEST_COMPANY_ID
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "content" in data[0]
    assert "metadata" in data[0]
    print(f"Search successful, found {len(data)} results. First result content snippet: {data[0]['content'][:50]}...")


@pytest.mark.parametrize("model_name", ["qwen2.5:7b", "llama3"])
def test_07_chat_with_ai_agent(client: httpx.Client, model_name: str):
    """Test chatting with the AI agent using different LLM models."""
    print(f"\n--- Test 07: Chat with AI Agent ({model_name}) ---")
    assert access_token is not None, "Access token not obtained from login test."
    response = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "question": f"What is the return policy? (using {model_name})",
            "company_id": TEST_COMPANY_ID,
            "agent_type": model_name # Use the parameterized model name
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert len(data["answer"]) > 0
    assert len(data["sources"]) > 0 # Should find sources from policy.txt
    print(f"Chat with {model_name} successful. Answer snippet: {data['answer'][:100]}...")


def test_08_data_analysis(client: httpx.Client):
    """Test the /analyze endpoint with a CSV file."""
    print("\n--- Test 08: Data Analysis ---")
    assert access_token is not None, "Access token not obtained from login test."
    assert os.path.exists(TEST_SALES_FILE_PATH), f"Test file not found: {TEST_SALES_FILE_PATH}"

    with open(TEST_SALES_FILE_PATH, "rb") as f:
        response = client.post(
            "/analyze",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": (os.path.basename(TEST_SALES_FILE_PATH), f, "text/csv")},
            data={
                "question": "What are the total sales for each product?",
                "debug": "true"
            }
        )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data # Changed from "answer" to "summary"
    assert "generated_code" in data # Changed from "code" in data["meta"]
    assert "table" in data # Changed from "result" in data["meta"]
    if data["summary"] is not None: # Check if summary is not None before checking length
        assert len(data["summary"]) > 0
        summary_snippet = data['summary'][:100]
    else:
        summary_snippet = "No summary provided."
    print(f"Data analysis successful. Summary snippet: {summary_snippet}...") # Changed from "answer" to "summary"
    print(f"Generated code snippet: {data['generated_code'][:100]}...")


def test_09_delete_document(client: httpx.Client):
    """Test deleting the uploaded document."""
    print("\n--- Test 09: Delete Document ---")
    global doc_id
    assert access_token is not None, "Access token not obtained from login test."
    assert doc_id is not None, "Document ID not obtained from upload test."

    response = client.delete(
        f"/documents/{doc_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"company_id": TEST_COMPANY_ID}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["doc_id"] == doc_id
    assert data["deleted_chunks"] > 0
    print(f"Document {doc_id} deleted successfully, {data['deleted_chunks']} chunks removed.")