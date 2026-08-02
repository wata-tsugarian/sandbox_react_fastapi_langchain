from app.ingestion.chunker import create_chunks
from app.ingestion.loader import load_documents
from app.middleware.vector_store import vector_store_client


def main():
    print("invoke開始")
    raw_documents = load_documents()
    chunks = create_chunks(raw_documents=raw_documents)
    print(f"{len(chunks)=}")

    vector_store_client.rebuild(chunks=chunks)


if __name__ == "__main__":
    main()
