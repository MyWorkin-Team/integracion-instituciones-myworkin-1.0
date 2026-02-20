from datetime import datetime, timezone
from app.domain.model.student import Student
from app.domain.port.student_repository_port import StudentRepositoryPort
from app.infrastructure.firebase.firebase_client import create_firebase_user, update_firebase_auth_user, set_firebase_user_claims
from app.shared.utils import generate_search_tokens

class UpsertStudentUseCase:

    def __init__(self, repo: StudentRepositoryPort):
        self.repo = repo

    def execute(self, student: Student) -> str:
        """
        Realiza un upsert del estudiante:
        1. Busca si ya existe por DNI.
        2. Si existe, actualiza Firestore y Auth.
        3. Si no existe, crea un nuevo usuario en Auth y Firestore.
        Retorna "created" o "updated".
        """
        existing = self.repo.find_by_dni(student.dni)

        if existing:
            # === UPDATE ===
            firebase_uid = existing.get("uid")
            if not firebase_uid:
                raise RuntimeError("Usuario existe en Firestore pero no tiene firebase_uid")

            # Actualizar Auth
            update_firebase_auth_user(
                app=self.repo.app,
                uid=firebase_uid,
                email=student.email,
                display_name=student.displayName,
            )

            # Actualizar Firestore
            data = student.to_firestore_dict()
            data["updatedAt"] = datetime.now(timezone.utc)
            self.repo.update_by_dni(student.dni, data)
            return "updated"

        else:
            # === CREATE ===
            # Generar ID del documento Firestore
            doc_ref = self.repo.collection.document()
            uid = doc_ref.id

            # Crear usuario en Firebase Auth
            create_firebase_user(
                app=self.repo.app,
                uid=uid,
                email=student.email,
                password=student.dni,  # DNI como password inicial
                display_name=student.displayName
            )

            # Asignar Custom Claims
            set_firebase_user_claims(
                app=self.repo.app,
                uid=uid,
                claims={"userType": "student"}
            )

            # Preparar datos
            student.uid = uid
            student.createdFrom = 'admin'
            student.createdAt = datetime.now(timezone.utc)
            student.updatedAt = student.createdAt
            student.searchTokens = generate_search_tokens(student.displayName)

            # Guardar en Firestore
            self.repo.save(uid, student)
            return "created"
