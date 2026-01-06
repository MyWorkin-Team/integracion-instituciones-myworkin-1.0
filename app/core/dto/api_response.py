from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

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
