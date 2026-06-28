from fastapi import FastAPI
from app.Back_End.api.routes import chat, search
from app.Back_End.api.routes import documents
from app.Back_End.api.routes import auth
from app.Back_End.api.routes import companies
from app.Back_End.db.session import engine, Base


Base.metadata.create_all(bind=engine)



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
