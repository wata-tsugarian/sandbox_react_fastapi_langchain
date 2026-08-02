from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=3000)

    @field_validator("prompt")
    @classmethod
    def not_blank(cls, value: str):
        if not value.strip():
            raise ValueError("プロンプトが空です。プロンプトを入力してください。")
        return value.strip()


class PromptResponse(BaseModel):
    response: str
