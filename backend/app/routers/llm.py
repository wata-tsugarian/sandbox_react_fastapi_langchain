import logging
from collections.abc import AsyncIterable

from fastapi import APIRouter, HTTPException
from fastapi.sse import EventSourceResponse

from app.generation.generator import generate_answer, generate_answer_stream
from app.schemas.prompt import PromptRequest, PromptResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/prompt", response_model=PromptResponse)
def llm_generate_answer(payload: PromptRequest):
    try:
        llm_answer = generate_answer(question=payload.prompt)
        return {
            "response": llm_answer,
        }
    except Exception as e:
        logger.exception("回答生成に失敗しました。")
        raise HTTPException(
            status_code=503,
            detail="LLMサーバーが接続されていません。",
        ) from e


@router.post("/prompt/stream", response_class=EventSourceResponse)
async def llm_generate_answer_stream(
    payload: PromptRequest,
) -> AsyncIterable[PromptResponse]:
    chunks = generate_answer_stream(question=payload.prompt)

    try:
        async for chunk in chunks:
            yield PromptResponse(response=chunk)
    except Exception:
        logger.exception("回答生成に失敗しました。")
        yield PromptResponse(response="LLMサーバーが接続されていません。")
