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
from starlette.responses import JSONResponse, HTMLResponse
import logging

from app.core.dto.api_response import validation_exception_handler
from app.core.limiter import limiter
from app.delivery.http.middlewares.ip_middleware import ApiKeyMiddleware
from app.infrastructure.firebase.firebase_exceptions import FirebaseConfigError

# Routers
from app.delivery.http.routers.student_router import router as student_router
from app.delivery.http.routers.company_router import router as company_router
from app.delivery.http.routers.jobs_router import router as jobs_router

# Sync
from app.infrastructure.sync.firebase_redis_sync import sync_all_universities

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title="Integración Instituciones - MyWorkIn",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

@app.get("/openapi-push.json", include_in_schema=False)
async def openapi_push():
    from fastapi.openapi.utils import get_openapi
    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    push_methods = {"post", "put", "patch"}
    allowed_paths = ("/api/students/push", "/api/companies/push")
    filtered_paths = {
        path: {method: op for method, op in methods.items() if method in push_methods}
        for path, methods in schema.get("paths", {}).items()
        if path in allowed_paths
    }
    schema["paths"] = {path: ops for path, ops in filtered_paths.items() if ops}
    for methods in schema["paths"].values():
        for op in methods.values():
            op["parameters"] = [
                p for p in op.get("parameters", [])
                if p.get("name") != "university_id"
            ]
    return schema

@app.get("/docs", include_in_schema=False)
async def scalar_docs():
    html = """
    <!doctype html>
    <html>
      <head>
        <title>Integración Instituciones - MyWorkIn</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <script
          id="api-reference"
          data-url="/openapi-push.json"
          data-configuration='{"theme":"purple","hideModels":true}'
        ></script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
      </body>
    </html>
    """
    return HTMLResponse(html)


@app.on_event("startup")
async def startup_event():
    """Sync Firebase data to Redis on startup"""
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Firebase→Redis sync on startup...")
    try:
        sync_all_universities()
        logger.info("✓ Firebase→Redis sync completed successfully")
    except Exception as e:
        logger.error(f"⚠️ Firebase→Redis sync failed: {str(e)}")
        # Don't fail startup if sync fails

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
