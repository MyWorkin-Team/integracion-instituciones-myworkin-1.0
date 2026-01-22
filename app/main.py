import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al PYTHONPATH
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
import logging

from app.core.dto.api_response import validation_exception_handler
from app.core.limiter import limiter
from app.delivery.http.middlewares.ip_middleware import IPAndApiKeyMiddleware

# Routers
from app.delivery.http.routers.student_router import router as student_router
from app.delivery.http.routers.test_router import router as test_router
from app.delivery.http.routers.health_router import router as health_router
from app.delivery.http.routers.employer_router import router as employer_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title="Integración Instituciones - MyWorkIn",
    version="1.0.0"
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
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
        content={
            "status": 429,
            "label": "Too Many Requests",
            "description": "Rate limit excedido",
            "body": {
                "error": "Too Many Requests",
                "message": "Has excedido el límite de peticiones permitidas. Intenta nuevamente más tarde."
            }
        }
    )
# 🔌 Routers
app.include_router(student_router, prefix="/api/students", tags=["Students"])
app.include_router(test_router, prefix="/test", tags=["Test"])
app.include_router(employer_router, prefix="/api/employers", tags=["Employers"])
app.include_router(health_router, tags=["Health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
