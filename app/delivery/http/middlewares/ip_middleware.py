from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# 🔐 IPs permitidas
ALLOWED_IPS = {
    "127.0.0.1",
    "localhost",
    "192.168.1.10",
}

class IPWhitelistMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host

        if client_ip not in ALLOWED_IPS:
            raise HTTPException(
                status_code=403,
                detail=f"IP {client_ip} not allowed"
            )

        return await call_next(request)
