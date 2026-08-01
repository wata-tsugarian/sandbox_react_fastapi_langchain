from langchain_community.document_loaders import GitLoader
from langchain_core.documents import Document


def is_mdx_file(file_path: str) -> bool:
    """mdx拡張子判定

    Args:
        file_path: 判定するfile

    Returns:
        判定結果: bool
    """
    return file_path.endswith(".mdx")


def load_documents() -> list[Document]:
    """ドキュメント読み込み

    Returns:
        読み込んだドキュメントのlist
    """
    loader = GitLoader(
        repo_path="./langchain_docs",
        clone_url="https://github.com/langchain-ai/docs",
        branch="main",
        file_filter=is_mdx_file,
    )

    return loader.load()
