from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_core.documents import Document


def create_chunks(raw_documents: list[Document]) -> list[Document]:
    """ドキュメントをチャンク化

    Args:
        raw_documents: 読み出した生ドキュメント

    Returns:
        チャンクしたドキュメントのlist
    """
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        Language.MARKDOWN,
        chunk_size=1000,
        chunk_overlap=200,
    )

    return text_splitter.split_documents(raw_documents)
