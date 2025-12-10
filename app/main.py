from fastapi import FastAPI
from app.delivery.routers.student_router import router

app = FastAPI(title="Students API - Hexagonal Firebase")
app.include_router(router)
