import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

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


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def _sse_stream(question: str) -> AsyncIterator[str]:
    try:
        async for chunk in generate_answer_stream(question=question):
            yield _sse(payload={"type": "chunk", "content": chunk})
    except Exception:
        logger.exception("ストリーミング生成に失敗しました。")
        yield _sse(
            payload={"type": "error", "message": "ストリーミング生成に失敗しました。"}
        )

    yield _sse(payload={"type": "done"})


@router.post("/prompt/stream")
async def llm_generate_answer_stream(payload: PromptRequest):
    return StreamingResponse(
        _sse_stream(question=payload.prompt),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
