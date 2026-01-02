import os
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("push_security")

ALLOWED_IPS = {
    "127.0.0.1",
    "::1",
    "192.168.18.8"
}

PUSH_API_KEY = os.getenv("PUSH_API_KEY", "dev-push-key")

# 🔐 RUTAS PROTEGIDAS (prefijos)
PROTECTED_PATHS = (
    "/api/students/push",            # /api/students/push/*
)

class IPAndApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        path = request.url.path
        logger.info(f"[SECURITY] Incoming request path: {path}")

        # 🔎 Verificar si la ruta es protegida
        is_protected = any(path.startswith(p) for p in PROTECTED_PATHS)

        if not is_protected:
            logger.info(f"[SECURITY] Skipping security for path: {path}")
            return await call_next(request)

        # 🧪 IP
        client_ip = request.headers.get("x-test-ip") or request.client.host
        api_key = request.headers.get("x-api-key")

        logger.warning(f"[SECURITY] PROTECTED PATH | IP={client_ip}")

        # 🚫 IP no permitida
        if client_ip not in ALLOWED_IPS:
            return JSONResponse(
                status_code=403,
                content={"detail": "IP not allowed"}
            )

        # 🔐 API KEY inválida
        if not api_key or api_key != PUSH_API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API Key"}
            )

        logger.info("[SECURITY] Access granted")
        return await call_next(request)
