from datetime import datetime, timezone
from app.domain.port.student_repository_port import StudentRepositoryPort

class UpdateStudentByCoIdPsUseCase:

    def __init__(self, repo: StudentRepositoryPort):
        self.repo = repo

    def execute(self, co_id_ps: str, data: dict) -> bool:
        # 🔥 Backend timestamp
        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        return self.repo.update_by_co_id_ps(co_id_ps, data)
