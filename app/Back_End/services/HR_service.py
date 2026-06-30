import requests

from app.Back_End.db.vector_store import search_documents
from app.Back_End.prompts.HR_prompt import (
    SYSTEM_PROMPT,
    build_prompt
)

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
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


def ask_hr(
    company_id: str,
    question: str
):
    """
    Retrieve relevant HR documents for one company
    and generate an answer.
    """

    # Search only inside this company's documents
    context, sources = search_documents(
        query=question,
        company_id=company_id
    )

    # Build the prompt
    prompt = build_prompt(
        context=context,
        question=question
    )

    # Generate answer
    answer = call_ollama(prompt)

    return {
        "answer": answer,
        "source": sources
    }