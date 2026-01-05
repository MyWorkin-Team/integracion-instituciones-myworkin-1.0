from abc import ABC, abstractmethod
from typing import Optional
from app.domain.model.employer import Employer

class EmployerRepositoryPort(ABC):

    @abstractmethod
    def save(self, employer: Employer) -> str:
        """Return created or updated"""
        pass

    @abstractmethod
    def find_by_tax_id(self, taxId: str) -> Optional[Employer]:
        pass

