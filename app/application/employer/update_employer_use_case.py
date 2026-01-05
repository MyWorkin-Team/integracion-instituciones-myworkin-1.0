from datetime import datetime, timezone
from app.domain.port.employer_repository_port import EmployerRepositoryPort


class UpdateEmployerByTaxIdUseCase:

    def __init__(self, repo: EmployerRepositoryPort):
        self.repo = repo

    def execute(self, tax_id: str, data: dict) -> bool:
        # 🔥 Backend timestamp
        data["lastModified"] = datetime.now(timezone.utc).isoformat()

        return self.repo.update_by_tax_id(tax_id, data)
