from fastapi import FastAPI
from app.api.routes import documents

app = FastAPI()

app.include_router(documents.router, prefix="/documents")


@app.get("/health")
def health():
    return {"status": "ok"}