from abc import ABC, abstractmethod
from typing import Optional
from app.domain.model.company import Company

class CompanyRepositoryPort(ABC):

    @abstractmethod
    def save(self, company: Company) -> str:
        """Return created or updated"""
        pass

    @abstractmethod
    def find_by_ruc(self, ruc: str) -> Optional[Company]:
        pass

    @abstractmethod
    def save_user_company_relation(self, relation: dict):
        """Guarda la relación entre un usuario y una empresa en la colección users_companies"""
        pass
