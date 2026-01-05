from app.domain.port.employer_repository_port import EmployerRepositoryPort
from app.domain.model.employer import Employer
from google.cloud.firestore import FieldFilter


class EmployerRepositoryAdapter(EmployerRepositoryPort):

    def __init__(self, client):
        self.client = client
        self.collection = client.collection("employers")  # 🔑 colección employers

    # -------------------------------------------------
    # CREATE / SAVE (merge)
    # -------------------------------------------------
    def save(self, employer: Employer) -> str:
        """
        Guarda por document ID = employer.id
        (igual que Student, merge=True)
        """
        ref = self.collection.document(employer.id)
        exists = ref.get().exists
        ref.set(employer.__dict__, merge=True)
        return "updated" if exists else "created"

    # -------------------------------------------------
    # GET BY taxId
    # -------------------------------------------------
    def find_by_tax_id(self, tax_id: str):
        docs = (
            self.collection
            .where(filter=FieldFilter("taxId", "==", tax_id))
            .limit(1)
            .stream()
        )

        docs = list(docs)
        if not docs:
            return None

        return docs[0].to_dict()

    # -------------------------------------------------
    # UPDATE BY taxId
    # -------------------------------------------------
    def update_by_tax_id(self, tax_id: str, data: dict) -> bool:
        docs = (
            self.collection
            .where(filter=FieldFilter("taxId", "==", tax_id))
            .limit(1)
            .stream()
        )

        docs = list(docs)
        if not docs:
            return False

        docs[0].reference.update(data)
        return True
