from app.domain.port.student_repository_port import StudentRepositoryPort
from typing import Optional
from app.domain.model.student import Student

class GetStudentByIdUseCase:

    def __init__(self, repo: StudentRepositoryPort):
        self.repo = repo

    def execute(self, student_id: str) -> Optional[dict]:
        return self.repo.find_by_id(student_id)
