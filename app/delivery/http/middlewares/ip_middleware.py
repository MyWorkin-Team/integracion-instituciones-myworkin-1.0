from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

from app.config.security import (
    ALLOWED_IPS,
    PROTECTED_PATHS,
    PUSH_API_KEY,
)

logger = logging.getLogger("push_security")

class IPAndApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        path = request.url.path
        # logger.info(f"[SECURITY] Incoming path: {path}")

        # 🔎 ¿Ruta protegida?
        is_protected = any(path.startswith(p) for p in PROTECTED_PATHS)

        if not is_protected:
            return await call_next(request)


        # 🧪 IP
        client_ip = request.headers.get("x-test-ip") or request.client.host
        api_key = request.headers.get("x-api-key")


        logger.warning(f"[SECURITY] Protected path | IP={client_ip}")
        # 🚫 IP no permitida
        if client_ip not in ALLOWED_IPS:
            return JSONResponse(
                status_code=403,
                content={
                    "status": 403,
                    "label": "Forbidden",
                    "description": "IP no permitida",
                    "body": {
                        "error": "Forbidden",
                        "message": "La IP desde la que se realiza la petición no está permitida."
                    }
                }
            )

        # 🔐 API KEY inválida
        if not api_key or api_key != PUSH_API_KEY:
            return JSONResponse(
                status_code=401,
                content={
                    "status": 401,
                    "label": "Unauthorized",
                    "description": "API key inválida",
                    "body": {
                        "error": "Unauthorized",
                        "message": "La API key es inválida o no fue enviada."
                    }
                }
            )

        # logger.info("[SECURITY] Access granted")
        return await call_next(request)
