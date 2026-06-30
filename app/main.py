from fastapi import FastAPI

from app.Back_End.api.routes.hr import router as hr_router
from app.Back_End.api.routes.auth import router as auth_router

app = FastAPI(
    title="Multi-Agent AI System"
)

app.include_router(hr_router)
app.include_router(auth_router)