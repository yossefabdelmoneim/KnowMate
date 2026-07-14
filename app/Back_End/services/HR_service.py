from app.Back_End.core.config import settings
from app.Back_End.core.llm import get_llm_client
from app.Back_End.db.vector_store import search_documents
from app.Back_End.prompts.HR_prompt import (
    SYSTEM_PROMPT,
    build_prompt
)
from app.Back_End.services.router import classify_query


CHAT_PROMPT = """
You are a friendly and professional HR assistant.

Respond naturally to the user's message.

User:
{question}

Assistant:
"""


def ask_hr(
    company_id: str,
    question: str,
    files: list[str] | None = None,
    user_id: str | None = None,
):
    """
    Handle HR requests using query routing.
    Classifies the question as GENERAL_CHAT or HR_QUERY.
    """

    query_type = classify_query(question)

    # General conversation — no RAG
    if query_type == "GENERAL_CHAT":
        prompt = CHAT_PROMPT.format(question=question)
        llm = get_llm_client()
        answer = llm.chat(user_prompt=prompt, system_prompt=SYSTEM_PROMPT)
        return {
            "answer": answer,
            "source": []
        }

    # HR question — search company documents
    context, sources = search_documents(
        query=question,
        company_id=company_id,
        file_names=files,
        user_id=user_id,
    )

    if files and context:
        file_list = "The user has uploaded the following files: " + ", ".join(files)
        context = [file_list] + context

    prompt = build_prompt(
        context=context,
        question=question
    )

    llm = get_llm_client()
    answer = llm.chat(user_prompt=prompt, system_prompt=SYSTEM_PROMPT)

    return {
        "answer": answer,
        "source": sources
    }