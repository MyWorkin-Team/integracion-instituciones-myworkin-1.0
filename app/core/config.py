from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(
    name="x-api-key",
    auto_error=False
)

def require_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="x-api-key header missing"
        )
    return api_key
