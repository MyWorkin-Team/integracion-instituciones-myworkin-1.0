from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

T = TypeVar("T")


class ApiError(BaseModel):
    code: str
    message: str


class ApiResponse(BaseModel, Generic[T]):
    status: int
    success: bool
    message: Optional[str] = None   # mensaje general
    result: Optional[str] = None    # created | updated
    data: Optional[T] = None
    error: Optional[ApiError] = None

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={
            "status": 400,
            "label": "Bad Request",
            "description": "Datos inválidos",
            "body": {
                "error": "Bad Request",
                "message": "El cuerpo de la petición contiene datos inválidos o mal formateados.",
                "details": exc.errors()  
            }
        }
    )
