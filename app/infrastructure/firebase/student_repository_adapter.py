from app.domain.port.student_repository_port import StudentRepositoryPort
from app.domain.model.student import Student

class StudentRepositoryAdapter(StudentRepositoryPort):

    def __init__(self, client):
        self.client = client

    def save(self, student: Student) -> str:
        ref = self.client.collection("students").document(student.id)
        exists = ref.get().exists
        ref.set(student.__dict__, merge=True)
        return "updated" if exists else "created"

    def find_by_id(self, student_id: str):
        doc = self.client.collection("students").document(student_id).get()
        return doc.to_dict() if doc.exists else None
