from app.infrastructure.firebase.firebase_client import init_firebase
from app.infrastructure.firebase.student_repository_adapter import StudentRepositoryAdapter
from app.application.student.upsert_student_use_case import UpsertStudentUseCase
from app.application.student.get_student_by_id_use_case import GetStudentByIdUseCase
from fastapi import Path
from fastapi.params import Depends

_repos_cache = {}

def get_firebase_app(university_id: str = Path(...)):
    """Inyecta la Firebase App completa (ulima, utrujillo, etc.)"""
    return init_firebase(university_id)

def get_student_repo(university_id: str = Path(...), app = Depends(get_firebase_app)):
    """Inyecta el repositorio pasándole la APP completa y usando cache"""
    if university_id not in _repos_cache:
        _repos_cache[university_id] = StudentRepositoryAdapter(app)
    return _repos_cache[university_id]

def upsert_student_use_case(repo = Depends(get_student_repo)):
    return UpsertStudentUseCase(repo)

def get_student_by_id_use_case(repo = Depends(get_student_repo)):
    return GetStudentByIdUseCase(repo)

def get_repo_di(repo = Depends(get_student_repo)):
    return repo