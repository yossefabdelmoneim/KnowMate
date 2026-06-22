from langchain_community.llms import Ollama
from sympy.physics.units import temperature


def get_llm():
    return Ollama(
        model = "llama3",
        base_url="http://localhost:11434",
        temperature=0.2
    )