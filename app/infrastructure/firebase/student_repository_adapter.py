from app.domain.port.student_repository_port import StudentRepositoryPort
from app.domain.model.student import Student
from google.cloud.firestore import FieldFilter

class StudentRepositoryAdapter(StudentRepositoryPort):

    def __init__(self, client):
        self.client = client
        self.collection = client.collection("students")  # ✅ CLAVE

    def save(self, student: Student) -> str:
        ref = self.collection.document(student.id)
        exists = ref.get().exists
        ref.set(student.__dict__, merge=True)
        return "updated" if exists else "created"

    def find_by_id(self, student_id: str):
        doc = self.collection.document(student_id).get()
        return doc.to_dict() if doc.exists else None

    def update_by_co_id_ps(self, co_id_ps: str, data: dict) -> bool:
        docs = (
            self.collection
            .where(filter=FieldFilter("coIdPs", "==", co_id_ps))
            .limit(1)
            .stream()
        )

        docs = list(docs)
        if not docs:
            return False

        docs[0].reference.update(data)
        return True
