from langchain_community.llms import Ollama


def get_llm(model_name="llama3"):
    if model_name == "marketing-agent":
        import uuid
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="marketing-model.gguf",
            base_url="https://moattta-marktieng-agent.hf.space/v1",
            api_key="empty",
            temperature=0.2,
            default_headers={"x-request-id": str(uuid.uuid4())}
        )
    else:
        return Ollama(
            model=model_name,
            base_url="http://localhost:11434",
            temperature=0.2
        )
