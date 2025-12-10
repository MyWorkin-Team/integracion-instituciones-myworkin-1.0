from app.infrastructure.firebase.firebase_client import get_firestore
from app.infrastructure.firebase.student_repository_adapter import StudentRepositoryAdapter
from app.application.student.register_student_use_case import RegisterStudentUseCase

def student_repo():
    return StudentRepositoryAdapter(get_firestore())

def register_student_use_case():
    return RegisterStudentUseCase(student_repo())

def repo_use_case():
    return student_repo()
