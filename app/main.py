from fastapi import FastAPI, Request
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from app.core.limiter import limiter
from app.delivery.http.routers.student_router import router as student_router
from app.delivery.http.middlewares.ip_middleware import IPWhitelistMiddleware

app = FastAPI(
    title="Integración Instituciones - MyWorkIn",
    version="1.0.0"
)

app.add_middleware(IPWhitelistMiddleware)

# Registrar limiter en el state
app.state.limiter = limiter

# Middleware SlowAPI
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )

# Routers
app.include_router(
    student_router,
    prefix="/api",
    tags=["Students"]
)

@app.get("/")
def health_check():
    return {"status": "ok"}
