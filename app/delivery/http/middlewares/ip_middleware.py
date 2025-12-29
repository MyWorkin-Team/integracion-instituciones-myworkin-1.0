import os
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("push_security")

ALLOWED_IPS = {
    "127.0.0.1",
    "::1",
}

PUSH_API_KEY = os.getenv("PUSH_API_KEY", "dev-push-key")

# 🔐 RUTAS PROTEGIDAS
PROTECTED_PATHS = (
    "/api"         # /push/*
)

class IPAndApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        path = request.url.path
        logger.info(f"[PUSH] Incoming request path: {path}")

        if not path.startswith("/api"):
            logger.info(f"[PUSH] Skipping security for path: {path}")
            return await call_next(request)

        client_ip = request.headers.get("x-test-ip") or request.client.host
        api_key = request.headers.get("x-api-key")

        logger.warning(f"[PUSH] PROTECTED PATH | IP={client_ip}")

        if client_ip not in ALLOWED_IPS:
            return JSONResponse(
                status_code=403,
                content={"detail": "IP not allowed"}
            )

        if not api_key or api_key != PUSH_API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API Key"}
            )

        logger.info("[PUSH] Access granted")
        return await call_next(request)
