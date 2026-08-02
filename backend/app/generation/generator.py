from langchain_core.prompts import ChatPromptTemplate

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


def generate_answer(question: str) -> str:
    """質問に対して回答を生成

    Args:
        question: ユーザーの質問

    Returns:
        生成した回答内容
    """
    chunks = search_chunks(question=question)
    if not chunks:
        return "参考情報が見つからないため分かりません。"

    context = "\n\n".join(doc.page_content for doc in chunks)

    chain = _PROMPT | ollama_client.llm

    response = chain.invoke({"context": context, "question": question})

    return str(response.content)
