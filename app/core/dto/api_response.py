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

def _translate_validation_message(msg: str, ctx: dict = None) -> str:
    # Keep validation messages in English
    return msg

def _serialize_errors(errors: list) -> list:
    result = []
    for error in errors:
        serializable = {}
        for key, value in error.items():
            if key == "input":
                continue
            elif key == "msg":
                ctx = error.get("ctx", {})
                serializable[key] = _translate_validation_message(value, ctx)
            elif key == "ctx" and isinstance(value, dict):
                serializable[key] = {
                    k: str(v) if isinstance(v, Exception) else v
                    for k, v in value.items()
                }
            else:
                serializable[key] = value
        result.append(serializable)
    return result


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={
            "status": 400,
            "label": "Bad Request",
            "description": "Invalid data",
            "body": {
                "error": "Bad Request",
                "message": "The request body contains invalid or malformed data.",
                "details": _serialize_errors(exc.errors())
            }
        }
    )
