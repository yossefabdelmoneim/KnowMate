from fastapi import FastAPI

from app.api.routes import chat
from app.api.routes import search
from app.api.routes import documents
from app.api.routes import auth
from app.api.routes import companies
from app.db.session import engine, Base
from app.db import models


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(documents.router, prefix="/documents")
app.include_router(search.router, prefix="/search")
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(companies.router, prefix="/companies", tags=["companies"])

app.include_router(chat.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
