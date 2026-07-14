from app.Back_End.core.llm import get_llm_client
from app.Back_End.prompts.customer_agent import (
    RAG_PROMPT, RAG_SYSTEM_PROMPT,
    GENERAL_FALLBACK_PROMPT, FALLBACK_SYSTEM_PROMPT,
)
from app.Back_End.prompts.marketing_agent import MARKETING_PROMPT, MARKETING_SYSTEM_PROMPT
from app.Back_End.services.retrieval import search_mmr


def format_docs(docs):
    formatted = []
    for i, doc in enumerate(docs):
        formatted.append(f"[Source {i + 1}]\n{doc.page_content}")
    return "\n\n".join(formatted)


SYSTEM_PROMPTS = {
    "general": RAG_SYSTEM_PROMPT,
    "marketing": MARKETING_SYSTEM_PROMPT,
}

PROMPTS = {
    "general": RAG_PROMPT,
    "marketing": MARKETING_PROMPT,
}


class RAGService:
    def __init__(self, prompt_type="general"):
        self.llm_client = get_llm_client()
        self.prompt_type = prompt_type

    def generate_answer(self, question: str, company_id: str, files: list[str] | None = None, user_id: str | None = None):
        q = question.strip().lower()
        greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
        if q in greetings or q in {g + "!" for g in greetings} or q in {g + "," for g in greetings}:
            return {
                "answer": "Hello! How can I help you today? Feel free to ask me about your documents.",
                "sources": []
            }

        docs = search_mmr(
            query=question,
            company_id=company_id,
            file_names=files,
            user_id=user_id,
        )

        context = format_docs(docs) if docs else ""

        if not context:
            prompt = GENERAL_FALLBACK_PROMPT.format(question=question)
            answer = self.llm_client.chat(
                user_prompt=prompt,
                system_prompt=FALLBACK_SYSTEM_PROMPT,
            )
            return {
                "answer": answer,
                "sources": []
            }

        if files:
            file_list = "The user has uploaded the following files: " + ", ".join(files)
            context = file_list + "\n\n" + context

        prompt_template = PROMPTS.get(self.prompt_type, RAG_PROMPT)
        prompt = prompt_template.format(
            context=context,
            question=question
        )

        system_prompt = SYSTEM_PROMPTS.get(self.prompt_type)
        answer = self.llm_client.chat(
            user_prompt=prompt,
            system_prompt=system_prompt,
        )

        seen = set()
        unique_sources = []
        for d in (docs or []):
            src = d.metadata.get("source") or ""
            if src not in seen:
                seen.add(src)
                unique_sources.append(src)
        return {
            "answer": answer,
            "sources": unique_sources,
        }