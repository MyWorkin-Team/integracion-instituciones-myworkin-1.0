from datetime import datetime, timezone
from app.domain.model.student import Student
from app.domain.port.student_repository_port import StudentRepositoryPort
from app.infrastructure.firebase.firebase_client import create_firebase_user

class RegisterStudentUseCase:

    def __init__(self, repo: StudentRepositoryPort):
        self.repo = repo

    def execute(self, student: Student):
        # Set timestamp in backend
        firebase_user = create_firebase_user(
            email=student.email,
            password=student.coIdPs,          # ⚠️ ver nota abajo
            display_name=student.displayName
        )

        student.created_at = datetime.now(timezone.utc).isoformat()
        return self.repo.save(student)
