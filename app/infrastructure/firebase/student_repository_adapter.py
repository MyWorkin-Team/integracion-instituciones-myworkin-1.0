from app.domain.port.student_repository_port import StudentRepositoryPort
from app.domain.model.student import Student
from google.cloud.firestore import FieldFilter
from firebase_admin import firestore
class StudentRepositoryAdapter(StudentRepositoryPort):

    def __init__(self, app):
        self.app = app 
        # Ahora firestore.client(app=app) funcionará correctamente
        self.client = firestore.client(app=app)
        self.collection = self.client.collection("users")

    def save(self, uid: str, student: Student) -> str:
        ref = self.collection.document(uid)
        exists = ref.get().exists
        ref.set(student.to_firestore_dict(), merge=True)
        return "updated" if exists else "created"

    def find_by_id(self,co_id_ps: str):
        doc = self.collection.document(co_id_ps).get()
        return doc.to_dict() if doc.exists else None
    
    def find_by_dni(self, dni: str):
        docs = (
            self.collection
            .where(filter=FieldFilter("dni", "==", dni))
            .limit(1)
            .stream()
        )

        docs = list(docs)
        if not docs:
            return None
        
        return docs[0].to_dict()
    
    

    def update_by_dni(self, dni: str, data: dict) -> bool:
        docs = (
            self.collection
            .where(filter=FieldFilter("dni", "==", dni))
            .limit(1)
            .stream()
        )

        docs = list(docs)
        if not docs:
            return False

        docs[0].reference.update(data)
        return True
