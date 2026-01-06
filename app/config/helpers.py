from datetime import date, datetime
from app.core.dto.api_response import ApiResponse, ApiError
from app.core.errors.api_errors import ApiErrorCode

from typing import Generic, TypeVar, Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic.generics import GenericModel
from app.shared.utils import serialize_firestore

def date_to_datetime(value):
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, datetime.min.time())
    return value


T = TypeVar("T")

class ApiError(BaseModel):
    code: str
    message: str

class ApiResponse(GenericModel, Generic[T]):
    status: int
    success: bool
    message: Optional[str] = None
    result: Optional[str] = None
    data: Optional[T] = None
    error: Optional[ApiError] = None


def ok(
    data: T,
    *,
    message: str,
    result: Optional[str] = None,
    status: int = 200
) -> JSONResponse:

    safe_data = serialize_firestore(data)  # 🔥 AUTOMÁTICO

    response = ApiResponse[T](
        status=status,
        success=True,
        message=message,
        result=result,
        data=safe_data
    )

    return JSONResponse(
        status_code=status,
        content=response.model_dump(exclude_none=True)  
    )


def fail(
    *,
    code: str,
    message: str,
    status: int = 400
) -> JSONResponse:

    response = ApiResponse(
        status=status,
        success=False,
        error=ApiError(
            code=code,
            message=message
        )
    )

    return JSONResponse(
        status_code=status,
        content=response.model_dump(exclude_none=True)  # 🔑
    )
