from datetime import datetime, timezone
from app.domain.model.student import Student
from app.domain.port.student_repository_port import StudentRepositoryPort
from app.infrastructure.firebase.firebase_client import create_firebase_user

class RegisterStudentUseCase:

    def __init__(self, repo: StudentRepositoryPort):
        self.repo = repo

    def execute(self, student: Student):

        # 1️⃣ Generar ID del documento Firestore
        doc_ref = self.repo.collection.document()
        uid = doc_ref.id

        try:
            # 2️⃣ Crear usuario en Firebase Auth usando ese UID
            firebase_user = create_firebase_user(
                app=self.repo.app,
                uid=uid,  # 👈 clave
                email=student.email,
                password=student.coIdPs,
                display_name=student.displayName
            )

            # 3️⃣ Setear datos
            student.uid = uid
            student.createdFrom = 'admin'
            student.created_at = datetime.now(timezone.utc).isoformat()

            # 4️⃣ Guardar documento con ese mismo ID
            return self.repo.save_with_id(uid, student)

        except Exception as e:
            # 🛡️ Rollback: borrar usuario en Auth si algo falla
            try:
                auth.delete_user(uid, app=self.repo.app)
            except:
                pass
            raise e
