import shutil
from itertools import batched
from pathlib import Path

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from app.ingestion.chunker import create_chunks
from app.ingestion.loader import load_documents

persist_directory = Path(__file__).parent.parent / "chroma_db"


def main():
    raw_documents = load_documents()
    chunks = create_chunks(raw_documents=raw_documents)
    print(f"{len(chunks)=}")

    shutil.rmtree(persist_directory, ignore_errors=True)
    embeddings = OllamaEmbeddings(model="bge-m3")
    vector_store = Chroma(
        embedding_function=embeddings,
        persist_directory=str(persist_directory),
    )

    for i, chunk_group in enumerate(batched(chunks, 100)):
        print(f"グループ_{i}: 処理中")
        vector_store.add_documents(documents=chunk_group)

    print(vector_store._collection.count())


if __name__ == "__main__":
    main()
