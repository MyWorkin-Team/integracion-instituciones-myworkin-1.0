from typing import Optional
from app.domain.port.employer_repository_port import EmployerRepositoryPort
from app.domain.model.employer import Employer


class GetEmployerByTaxIdUseCase:

    def __init__(self, repo: EmployerRepositoryPort):
        self.repo = repo

    def execute(self, tax_id: str) -> Optional[Employer]:
        return self.repo.find_by_tax_id(tax_id)
