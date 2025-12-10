from abc import ABC, abstractmethod
from typing import Optional
from app.domain.model.student import Student

class StudentRepositoryPort(ABC):

    @abstractmethod
    def save(self, student: Student) -> str:
        """Return created or updated"""
        pass

    @abstractmethod
    def find_by_id(self, student_id: str) -> Optional[Student]:
        pass

