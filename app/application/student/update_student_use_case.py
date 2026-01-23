from datetime import datetime, timezone
from app.domain.model.student import Student
from app.domain.port.student_repository_port import StudentRepositoryPort
from app.infrastructure.firebase.firebase_client import update_firebase_auth_user

class UpdateStudentByCoIdPsUseCase:

    def __init__(self, repo: StudentRepositoryPort):
        self.repo = repo

    def execute(self, student: Student) -> bool:

        existing = self.repo.find_by_coIdPs(student.coIdPs)

        if not existing:
            return False

        firebase_uid = existing.get("uid")

        if not firebase_uid:
            raise RuntimeError(
                "Usuario existe en Firestore pero no tiene firebase_uid"
            )
        # ✅ CORRECCIÓN: Pasamos self.repo.app como primer argumento
        update_firebase_auth_user(
            app=self.repo.app,         # <--- Se requiere para saber qué universidad es
            uid=firebase_uid,          
            email=student.email,
            display_name=student.displayName,
        )

        # 3️⃣ Actualizar Firestore
        data = student.to_firestore_dict()
        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        self.repo.update_by_co_id_ps(student.coIdPs, data)

        return True