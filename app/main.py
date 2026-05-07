from fastapi import FastAPI

from app.api.routes import chat
from app.api.routes import search
from app.api.routes import documents

app = FastAPI()

app.include_router(documents.router, prefix="/documents")
app.include_router(search.router, prefix="/search")

app.include_router(chat.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}