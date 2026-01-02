from app.domain.port.student_repository_port import StudentRepositoryPort
from typing import Optional
from app.domain.model.student import Student

class GetStudentByIdUseCase:

    def __init__(self, repo: StudentRepositoryPort):
        self.repo = repo

    def execute(self,co_id_ps: str) -> Optional[Student]:
        return self.repo.find_by_coIdPs(co_id_ps)
