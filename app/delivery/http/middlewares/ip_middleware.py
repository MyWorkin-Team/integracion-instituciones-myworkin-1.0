import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

from app.config.security import (
    PROTECTED_PATHS,
    UNIVERSITY_API_KEYS,
    ALLOWED_UNIVERSITIES,
)

class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # 🔎 ¿Ruta protegida?
        is_protected = any(path.startswith(p) for p in PROTECTED_PATHS)

        if not is_protected:
            return await call_next(request)

        # 🔐 Obtener API Key de cabecera
        api_key_received = request.headers.get("x-api-key")

        if not api_key_received:
            return self._unauthorized("x-api-key header missing")

        # 🔍 Obtener university_id (desde body en POST/PUT)
        university_id = None
        if request.method in ["POST", "PUT"]:
            try:
                # Leemos el body sin consumirlo permanentemente
                body_bytes = await request.body()
                if body_bytes:
                    body_json = json.loads(body_bytes)
                    university_id = body_json.get("university_id")
                
                # Re-crear el request para que el siguiente handler pueda leer el body
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive
                
            except Exception as e:
                logger.error(f"Error parsing body in middleware: {e}")

        if not university_id:
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "label": "Bad Request",
                    "description": "university_id missing",
                    "body": {"error": "Bad Request", "message": "university_id es requerido en el body."}
                }
            )

        # ✅ Validar que la universidad esté en la lista de permitidas
        university_id_upper = university_id.upper()
        if university_id_upper not in ALLOWED_UNIVERSITIES:
            return self._unauthorized(f"Universidad '{university_id}' no está autorizada.")

        # 🔑 Verificar Key para esa universidad
        expected_key = UNIVERSITY_API_KEYS.get(university_id_upper)
        if not expected_key or api_key_received != expected_key:
            return self._unauthorized("API key inválida para la universidad especificada.")

        return await call_next(request)

    def _unauthorized(self, message: str):
        return JSONResponse(
            status_code=401,
            content={
                "status": 401,
                "label": "Unauthorized",
                "description": "Acceso denegado",
                "body": {"error": "Unauthorized", "message": message}
            }
        )
