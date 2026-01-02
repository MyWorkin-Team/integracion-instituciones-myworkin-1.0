from app.infrastructure.firebase.firebase_client import get_firestore
from app.infrastructure.firebase.student_repository_adapter import StudentRepositoryAdapter
from app.application.student.register_student_use_case import RegisterStudentUseCase
from app.application.student.update_student_use_case import UpdateStudentByCoIdPsUseCase
from app.application.student.get_student_by_id_use_case import GetStudentByIdUseCase

def student_repo():
    return StudentRepositoryAdapter(get_firestore())

def register_student_use_case():
    return RegisterStudentUseCase(student_repo())

def update_by_co_id_ps_use_case():
    return UpdateStudentByCoIdPsUseCase(student_repo())

def get_student_by_id_use_case():
    return GetStudentByIdUseCase(student_repo())

def repo_use_case():
    return student_repo()