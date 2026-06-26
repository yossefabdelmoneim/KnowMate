from fastapi import FastAPI

from Back_End.api import chat, search
from Back_End.api.routes import documents

app = FastAPI()

app.include_router(documents.router, prefix="/documents")
app.include_router(search.router, prefix="/search")

app.include_router(chat.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}