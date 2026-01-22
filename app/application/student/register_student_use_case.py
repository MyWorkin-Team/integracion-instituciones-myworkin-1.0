from datetime import datetime, timezone
from app.domain.model.student import Student
from app.domain.port.student_repository_port import StudentRepositoryPort
from app.infrastructure.firebase.firebase_client import create_firebase_user

class RegisterStudentUseCase:

    def __init__(self, repo: StudentRepositoryPort):
        self.repo = repo

    def execute(self, student: Student):
        # 1️⃣ Crear usuario en Firebase Auth
        firebase_user = create_firebase_user(
            app=self.repo.app,
            email=student.email,
            password=student.coIdPs,
            display_name=student.displayName
        )
        
        student.uid = firebase_user["uid"]
        # 2️⃣ Set timestamps
        student.created_at = datetime.now(timezone.utc).isoformat()

        # 3️⃣ Guardar UID de Firebase en Firestore
        return self.repo.save(student)
