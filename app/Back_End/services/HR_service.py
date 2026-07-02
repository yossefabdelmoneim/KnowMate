from app.Back_End.core.config import settings
from app.Back_End.core.llm import get_llm_client
from app.Back_End.db.vector_store import search_documents
from app.Back_End.prompts.HR_prompt import (
    SYSTEM_PROMPT,
    build_prompt
)


def ask_hr(
    company_id: str,
    question: str,
    files: list[str] | None = None,
):
    """
    Retrieve relevant HR documents for one company
    and generate an answer.
    """

    # Search only inside this company's documents
    context, sources = search_documents(
        query=question,
        company_id=company_id,
        file_names=files,
    )

    if not context:
        return {
            "answer": "I couldn't find this information in the HR documentation.",
            "source": []
        }

    if files:
        file_list = "The user has uploaded the following files: " + ", ".join(files)
        context = [file_list] + context

    # Build the prompt
    prompt = build_prompt(
        context=context,
        question=question
    )

    # Generate answer using the shared LLM client
    llm = get_llm_client()
    answer = llm.chat(user_prompt=prompt, system_prompt=SYSTEM_PROMPT)

    return {
        "answer": answer,
        "source": sources
    }