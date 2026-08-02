from langchain_core.documents import Document

from app.middleware.vector_store import vector_store_client


def search_chunks(question: str) -> list[Document]:
    return vector_store_client.search(question=question)
