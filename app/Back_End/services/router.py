from app.Back_End.core.llm import get_llm_client

HR_KEYWORDS = [
    "policy", "policies", "leave", "vacation", "annual leave",
    "sick leave", "attendance", "payroll", "salary", "benefits",
    "employee", "probation", "notice period", "working hours",
    "holiday", "overtime", "compensatory", "comp off", "hr",
    "promotion", "resignation", "termination",
]

CLASSIFY_PROMPT = """
You are a query classifier. Classify the user's message into ONLY ONE label: GENERAL_CHAT or HR_QUERY.

Rules:
- Return ONLY the label. Do NOT explain or answer the question.
- GENERAL_CHAT: greetings, casual conversation, thanks, who-are-you, what-can-you-do, etc.
- HR_QUERY: questions about HR policies, leave, salary, benefits, attendance, etc.

Examples:
User: Hi
GENERAL_CHAT

User: Hello, how are you?
GENERAL_CHAT

User: What can you do?
GENERAL_CHAT

User: Tell me about annual leave.
HR_QUERY

User: What is the leave policy?
HR_QUERY

User: How many sick days do I get?
HR_QUERY

User: What are the employee benefits?
HR_QUERY

User: Explain the probation period.
HR_QUERY

User:
{question}
"""


def classify_query(question: str) -> str:
    llm = get_llm_client()
    prompt = CLASSIFY_PROMPT.format(question=question)
    label = llm.chat(user_prompt=prompt).strip().upper()

    if "HR_QUERY" in label:
        return "HR_QUERY"

    question_lower = question.lower()
    for keyword in HR_KEYWORDS:
        if keyword in question_lower:
            return "HR_QUERY"

    return "GENERAL_CHAT"
