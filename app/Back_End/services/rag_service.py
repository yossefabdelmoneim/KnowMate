from app.Back_End.core.llm import get_llm_client
from app.Back_End.prompts.customer_agent import RAG_PROMPT
from app.Back_End.services.retrieval import search_mmr


def format_docs(docs):
    formatted = []
    for i, doc in enumerate(docs):
        formatted.append(f"[Source {i + 1}]\n{doc.page_content}")
    return "\n\n".join(formatted)


class RAGService:
    def __init__(self, agent_type="default"):
        # get_llm_client returns an LLMClient instance, which handles model selection internally
        self.llm_client = get_llm_client()

    def generate_answer(self, question: str, company_id: str):
        docs = search_mmr(
            query=question,
            company_id=company_id
        )

        if not docs:
            return {
                "answer": "No relevant information found.",
                "sources": []
            }

        context = format_docs(docs)

        # basic context trimming (important)
        context = context[:4000]

        prompt = RAG_PROMPT.format(
            context=context,
            question=question
        )

        # Use the chat method of the LLMClient
        answer = self.llm_client.chat(user_prompt=prompt)

        return {
            "answer": answer,
            "sources": [
                {
                    "doc_id": d.metadata.get("doc_id"),
                    "chunk_id": d.metadata.get("chunk_id")
                }
                for d in docs
            ]
        }