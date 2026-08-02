import logging

from fastapi import APIRouter, HTTPException

from app.generation.generator import generate_answer
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
