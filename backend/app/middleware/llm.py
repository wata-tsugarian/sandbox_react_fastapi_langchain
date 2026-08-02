from langchain_ollama import ChatOllama


class LLMClient:
    def __init__(self) -> None:
        self.llm = ChatOllama(
            model="llama3.1",
            temperature=0,
        )


ollama_client = LLMClient()
