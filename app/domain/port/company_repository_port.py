from abc import ABC, abstractmethod
from typing import Optional
from app.domain.model.company import Company

class CompanyRepositoryPort(ABC):

    @abstractmethod
    def save(self, company: Company) -> str:
        """Return created or updated"""
        pass

    @abstractmethod
    def find_by_ruc(self, ruc: str) -> Optional[dict]:
        pass

    @abstractmethod
    def update_by_ruc(self, ruc: str, data: dict) -> bool:
        pass

    @abstractmethod
    def save_user_company_relation(self, relation: dict):
        """Guarda la relación entre un usuario y una empresa en la colección users_companies"""
        pass

    @abstractmethod
    def find_user_company_by_email(self, email: str) -> Optional[dict]:
        """Busca un usuario en la colección users_companies por email"""
        pass

    @abstractmethod
    def find_user_company_by_email_and_role(self, company_id: str, role: str) -> Optional[dict]:
        """Busca un usuario en la colección users_companies por companyId y role"""
        pass

    @abstractmethod
    def update_user_company_email(self, user_company_id: str, new_email: str) -> bool:
        """Actualiza el email de un usuario en la colección users_companies"""
        pass

    @abstractmethod
    def get_next_user_company_id(self) -> str:
        """Genera un nuevo ID para la colección users_companies"""
        pass
