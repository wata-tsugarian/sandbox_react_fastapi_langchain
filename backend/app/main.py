from fastapi import FastAPI

from app.routers.llm import router as llm_router
from app.settings import settings

app = FastAPI()


@app.get("/")
def read_root():
    return {
        "env": settings.env,
        "message": "Hello, World!",
    }


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


app.include_router(llm_router)
