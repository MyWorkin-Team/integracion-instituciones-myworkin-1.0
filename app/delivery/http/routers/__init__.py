from .student_router import router as student_router
from .test_router import router as test_router
from .health_router import router as health_router
__all__ = [
    "student_router",
    "test_router",
    "health_router"
]
