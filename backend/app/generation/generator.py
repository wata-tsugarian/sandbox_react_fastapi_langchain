from collections.abc import AsyncIterator

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from starlette.concurrency import run_in_threadpool

from app.middleware.llm import ollama_client
from app.retrieval.retriever import search_chunks

_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """あなたは与えられた「参考情報」だけを根拠に回答するアシスタントです。
- 参考情報に答えがある場合のみ、その内容に基づいて回答してください。
- 参考情報に答えが見つからない場合は、推測せず「情報が見つからないため分かりません」とだけ回答してください。
- 参考情報に書かれていない知識は使わないでください。
""",
        ),
        ("user", "参考情報: {context}\n\n質問: {question}"),
    ]
)

_CHAIN = _PROMPT | ollama_client.llm | StrOutputParser()

_NOT_FOUND_MESSAGE = "参考情報が見つからないため分かりません。"


def _build_context(chunks: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in chunks)


def generate_answer(question: str) -> str:
    """質問に対して回答を生成

    Args:
        question: ユーザーの質問

    Returns:
        生成した回答内容
    """
    chunks = search_chunks(question=question)
    if not chunks:
        return _NOT_FOUND_MESSAGE

    context = _build_context(chunks=chunks)

    response = _CHAIN.invoke({"context": context, "question": question})

    return response


async def generate_answer_stream(question: str) -> AsyncIterator[str]:
    """質問に対して回答をストリーミング生成

    Args:
        question: ユーザーの質問

    Yields:
        生成した回答内容のイテレーター
    """
    chunks = await run_in_threadpool(search_chunks, question=question)
    if not chunks:
        yield _NOT_FOUND_MESSAGE
        return

    context = _build_context(chunks=chunks)

    async for chunk in _CHAIN.astream({"context": context, "question": question}):
        yield chunk
