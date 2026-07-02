from app.Back_End.core.llm import get_llm_client
from app.Back_End.prompts.customer_agent import RAG_PROMPT
from app.Back_End.prompts.marketing_agent import MARKETING_PROMPT
from app.Back_End.services.retrieval import search_mmr


def format_docs(docs):
    formatted = []
    for i, doc in enumerate(docs):
        formatted.append(f"[Source {i + 1}]\n{doc.page_content}")
    return "\n\n".join(formatted)


PROMPTS = {
    "general": RAG_PROMPT,
    "marketing": MARKETING_PROMPT,
}


class RAGService:
    def __init__(self, prompt_type="general"):
        self.llm_client = get_llm_client()
        self.prompt_type = prompt_type

    def generate_answer(self, question: str, company_id: str, files: list[str] | None = None):
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
        )

        context = format_docs(docs) if docs else ""

        if not context:
            return {
                "answer": "No relevant information found. Please upload a document first.",
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

        answer = self.llm_client.chat(user_prompt=prompt)

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