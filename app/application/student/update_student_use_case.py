from datetime import datetime, timezone
from app.domain.model.student import Student
from app.domain.port.student_repository_port import StudentRepositoryPort
from app.infrastructure.firebase.firebase_client import update_firebase_user

class UpdateStudentByCoIdPsUseCase:

    def __init__(self, repo: StudentRepositoryPort):
        self.repo = repo

    def execute(self, co_id_ps: str, student: Student) -> bool:

        # # 🔥 1️⃣ Actualizar Firebase (igual que en Register)
        # update_firebase_user(
        #     uid=student.firebase_uid,
        #     email=student.email,
        #     display_name=student.displayName,
        # )

        # 🔥 2️⃣ Actualizar Firestore
        data = student.to_firestore_dict()
        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        return self.repo.update_by_co_id_ps(co_id_ps, data)
