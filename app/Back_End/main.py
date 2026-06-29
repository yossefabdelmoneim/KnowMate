from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.Back_End.api.routes import chat, search
from app.Back_End.api.routes import documents
from app.Back_End.api.routes import auth
from app.Back_End.api.routes import companies
from app.Back_End.db.session import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KnowMate API",
    description="Knowledge Management and AI Assistant API for enterprises",
    version="1.0.0",
    contact={
        "name": "KnowMate Support",
        "url": "https://knowmate.example.com",
        "email": "support@knowmate.example.com",
    },
    license_info={
        "name": "MIT",
    },
)

app.include_router(documents.router, prefix="/documents")
app.include_router(search.router, prefix="/search")
app.include_router(auth.router, prefix="/auth")
app.include_router(companies.router, prefix="/companies")
app.include_router(chat.router, prefix="/api")


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "ok"}
                }
            }
        }
    }
)
def health():
    """
    Health check endpoint to verify API is running.
    
    Returns a simple status response if the API is operational.
    """
    return {"status": "ok"}
