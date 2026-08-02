import shutil
from itertools import batched
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings


class VectorStoreClient:
    def __init__(self) -> None:
        self.embeddings = OllamaEmbeddings(model="bge-m3")
        self.persist_dir = Path(__file__).parent.parent / "chroma_db"
        self._store = None

    def _get_store(self) -> Chroma:
        if self._store is None:
            self._store = Chroma(
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_dir),
            )

        return self._store

    def search(self, question: str, k: int = 3) -> list[Document]:
        return self._get_store().similarity_search(query=question, k=k)

    def rebuild(self, chunks: list[Document]) -> None:
        shutil.rmtree(self.persist_dir, ignore_errors=True)
        store = Chroma(
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_dir),
        )
        for i, chunk_group in enumerate(batched(chunks, 2000)):
            print(f"グループ_{i}: 処理中")
            store.add_documents(documents=chunk_group)

        print(f"{store._collection.count()=}")


vector_store_client = VectorStoreClient()
