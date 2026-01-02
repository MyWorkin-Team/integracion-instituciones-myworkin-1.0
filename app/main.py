from fastapi import FastAPI, Request
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
import logging

from app.core.limiter import limiter
from app.delivery.http.middlewares.ip_middleware import IPAndApiKeyMiddleware

# Routers
from app.delivery.http.routers.student_router import router as student_router
from app.delivery.http.routers.test_router import router as test_router
from app.delivery.http.routers.health_router import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title="Integración Instituciones - MyWorkIn",
    version="1.0.0"
)

# 🔐 Middlewares
app.add_middleware(IPAndApiKeyMiddleware)

# Rate limit
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )

# 🔌 Routers
app.include_router(student_router, prefix="/api/students", tags=["Students"])
app.include_router(test_router, prefix="/test", tags=["Test"])
app.include_router(health_router, tags=["Health"])
