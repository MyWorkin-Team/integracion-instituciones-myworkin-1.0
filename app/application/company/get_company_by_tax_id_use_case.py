from typing import Optional
from app.domain.port.company_repository_port import CompanyRepositoryPort
from app.domain.model.company import Company


class GetCompanyByTaxIdUseCase:

    def __init__(self, repo: CompanyRepositoryPort):
        self.repo = repo

    def execute(self, ruc: str) -> Optional[Company]:
        return self.repo.find_by_ruc(ruc)
