from app.domain.port.company_repository_port import CompanyRepositoryPort
from app.domain.model.company import Company
from google.cloud.firestore import FieldFilter
from firebase_admin import firestore
from typing import Optional

class CompanyRepositoryAdapter(CompanyRepositoryPort):

    def __init__(self, app):
        self.app = app 
        self.client = firestore.client(app=app)
        self.collection = self.client.collection("companies")
        self.users_companies_collection = self.client.collection("users_companies")

    # -------------------------------------------------
    # SAVE USER-COMPANY RELATION
    # -------------------------------------------------
    def save_user_company_relation(self, relation: dict):
        relation["createdFromAdmin"] = True
        now = firestore.SERVER_TIMESTAMP

        relation["createdAt"] = relation.get("createdAt") or now
        relation["updatedAt"] = now

        email = relation.get("email")
        company_id = relation.get("companyId")

        if not email or not company_id:
            raise ValueError("email y companyId son obligatorios")

        # 🔎 Verificar si ya existe la relación
        query = (
            self.users_companies_collection
            .where(filter=FieldFilter("email", "==", email))
            .where(filter=FieldFilter("companyId", "==", company_id))
            .limit(1)
            .stream()
        )

        existing = list(query)

        if existing:
            # Ya existe → actualizamos
            doc = existing[0]
            relation["uid"] = doc.id
            doc.reference.set(relation, merge=True)
            return doc.id

        # 🚀 Si no existe → crear nuevo
        uid = relation.get("uid")
        if uid:
            doc_ref = self.users_companies_collection.document(uid)
        else:
            doc_ref = self.users_companies_collection.document()
            relation["uid"] = doc_ref.id
            
        doc_ref.set(relation)

        return doc_ref.id

    def get_next_user_company_id(self) -> str:
        """Genera un nuevo ID para la colección users_companies"""
        return self.users_companies_collection.document().id
    
    # -------------------------------------------------
    # CREATE / SAVE (merge)
    # -------------------------------------------------
    def save(self, company: Company) -> str:
        """
        Guarda por document ID = company.id
        (igual que Student, merge=True)
        """
        ref = self.collection.document(company.id)
        exists = ref.get().exists
        # Usamos el método to_firestore_dict si existe o convertimos a dict
        data = company.to_firestore_dict() if hasattr(company, 'to_firestore_dict') else company.__dict__
        ref.set(data, merge=True)
        return "updated" if exists else "created"

    # -------------------------------------------------
    # GET BY ruc
    # -------------------------------------------------
    def find_by_ruc(self, ruc: str):
        docs = (
            self.collection
            .where(filter=FieldFilter("ruc", "==", ruc))
            .limit(1)
            .stream()
        )

        docs = list(docs)
        if not docs:
            return None

        # Incluimos el ID del documento en el diccionario retornado
        data = docs[0].to_dict()
        data["id"] = docs[0].id
        return data

    # -------------------------------------------------
    # UPDATE BY ruc (legacy/internal use)
    # -------------------------------------------------
    def update_by_ruc(self, ruc: str, data: dict) -> bool:
        docs = (
            self.collection
            .where(filter=FieldFilter("ruc", "==", ruc))
            .limit(1)
            .stream()
        )

        docs = list(docs)
        if not docs:
            return False

        docs[0].reference.update(data)
        return True

    # -------------------------------------------------
    # FIND USER-COMPANY BY EMAIL
    # -------------------------------------------------
    def find_user_company_by_email(self, email: str) -> Optional[dict]:
        """Busca un usuario en la colección users_companies por email"""
        docs = (
            self.users_companies_collection
            .where(filter=FieldFilter("email", "==", email))
            .limit(1)
            .stream()
        )

        docs = list(docs)
        if not docs:
            return None

        data = docs[0].to_dict()
        data["id"] = docs[0].id
        return data
