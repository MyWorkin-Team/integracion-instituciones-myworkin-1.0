from datetime import datetime, timezone
from app.domain.model.employer import Employer
from app.domain.port.employer_repository_port import EmployerRepositoryPort


class RegisterEmployerUseCase:

    def __init__(self, repo: EmployerRepositoryPort):
        self.repo = repo

    def execute(self, employer: Employer):
        # ⏱️ Timestamp backend
        return self.repo.save(employer)
