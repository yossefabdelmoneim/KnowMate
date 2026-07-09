import requests

from app.Back_End.db.vector_store import search_documents
from app.Back_End.prompts.HR_prompt import (
    SYSTEM_PROMPT,
    build_prompt
)
from app.Back_End.services.router import classify_query

MODEL_NAME = "qwen2.5:1.5b"


def call_ollama(prompt: str) -> str:
    """
    Send the prompt to the Qwen model running on Ollama.
    """

    response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0
        }
    }
)

    response.raise_for_status()

    return response.json()["message"]["content"]


def ask_hr(
    company_id: str,
    question: str
):
    """
    Handle HR requests using query routing.
    """

    # Step 1: Classify the user's message
    query_type = classify_query(question)

    print("=" * 60)
    print("Question:", question)
    print("Query Type:", query_type)
    print("=" * 60)

    # Step 2: General conversation (No RAG)
    if query_type == "GENERAL_CHAT":

        prompt = f"""
You are a friendly and professional HR assistant.

Respond naturally to the user's message.

Examples:
User: Hi
Assistant: Hello! 👋 How can I help you today?

User: How are you?
Assistant: I'm doing well, thank you! How can I assist you with your HR questions today?

User: What can you do?
Assistant: I can help answer questions about your company's HR policies, leave, attendance, payroll, benefits, and other HR-related topics.

User:
{question}

Assistant:
"""

        answer = call_ollama(prompt)

        return {
            "answer": answer,
            "source": []
        }

    # Step 3: HR Question → Search company documents
    context, sources = search_documents(
        query=question,
        company_id=company_id
    )

    print("Context Length:", len(context))
    if context:
        print("\nFirst Retrieved Chunk:\n")
        print(context[0])
        print("-" * 60)

    # Step 4: Build the RAG prompt
    prompt = build_prompt(
        context=context,
        question=question
    )

    # Step 5: Generate answer
    answer = call_ollama(prompt)

    return {
        "answer": answer,
        "source": sources
    }