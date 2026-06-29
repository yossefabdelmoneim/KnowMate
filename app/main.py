from fastapi import FastAPI

from app.Back_End.api.routes.hr import router as hr_router

app = FastAPI(
    title="Multi-Agent AI System"
)

app.include_router(hr_router)