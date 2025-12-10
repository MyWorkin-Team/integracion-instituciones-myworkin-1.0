from datetime import datetime, timezone
from app.domain.model.student import Student
from app.domain.port.student_repository_port import StudentRepositoryPort

class RegisterStudentUseCase:

    def __init__(self, repo: StudentRepositoryPort):
        self.repo = repo

    def execute(self, student: Student):
        # Set timestamp in backend
        student.created_at = datetime.now(timezone.utc).isoformat()
        return self.repo.save(student)
