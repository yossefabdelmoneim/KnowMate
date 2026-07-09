import requests

MODEL_NAME = "qwen2.5:1.5b"


HR_KEYWORDS = [
    "policy",
    "policies",
    "leave",
    "vacation",
    "annual leave",
    "sick leave",
    "attendance",
    "payroll",
    "salary",
    "benefits",
    "employee",
    "probation",
    "notice period",
    "working hours",
    "holiday",
    "overtime",
    "compensatory",
    "comp off",
    "hr",
    "promotion",
    "resignation",
    "termination",
]


def classify_query(question: str) -> str:

    prompt = f"""
You are a query classifier.

Classify the user's message into ONLY ONE label.

GENERAL_CHAT
HR_QUERY

Rules:
- Return ONLY one label.
- Do NOT explain.
- Do NOT answer the question.
- Do NOT write anything except the label.

Examples:

User: Hi
GENERAL_CHAT

User: Hello
GENERAL_CHAT

User: Hey there!
GENERAL_CHAT

User: Good morning
GENERAL_CHAT

User: How are you?
GENERAL_CHAT

User: Thanks
GENERAL_CHAT

User: Bye
GENERAL_CHAT

User: Who are you?
GENERAL_CHAT

User: What can you do?
GENERAL_CHAT

User: Tell me about annual leave.
HR_QUERY

User: What is the leave policy?
HR_QUERY

User: How many annual leave days?
HR_QUERY

User: Explain the sick leave policy.
HR_QUERY

User: What is the policy for availing compensatory off?
HR_QUERY

User: Tell me about attendance policy.
HR_QUERY

User: What are employee benefits?
HR_QUERY

User: What is the probation period?
HR_QUERY

User:
{question}
"""

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }
    )

    response.raise_for_status()

    label = response.json()["message"]["content"].strip().upper()

    # لو الموديل قال HR خلاص
    if "HR_QUERY" in label:
        return "HR_QUERY"

    # Verification
    question_lower = question.lower()

    for keyword in HR_KEYWORDS:
        if keyword in question_lower:
            return "HR_QUERY"

    return "GENERAL_CHAT"