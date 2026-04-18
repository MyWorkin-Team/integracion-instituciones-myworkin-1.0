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
from app.delivery.http.middlewares.ip_middleware import ApiKeyMiddleware
from app.infrastructure.firebase.firebase_exceptions import FirebaseConfigError

# Routers
from app.delivery.http.routers.student_router import router as student_router
from app.delivery.http.routers.company_router import router as company_router
from app.delivery.http.routers.jobs_router import router as jobs_router

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

@app.exception_handler(FirebaseConfigError)
async def firebase_config_error_handler(request: Request, exc: FirebaseConfigError):
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "label": "Internal Server Error",
            "description": "Error en la configuración de Firebase",
            "body": {
                "error": "Firebase Configuration Error",
                "message": str(exc)
            }
        }
    )

# 🔐 Middlewares
app.add_middleware(ApiKeyMiddleware)

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
app.include_router(company_router, prefix="/api/companies", tags=["Companies"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
