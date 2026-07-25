from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    環境変数を管理するSettingsクラス
    """

    # ENV
    env: str = Field(default="local")


settings = Settings()
