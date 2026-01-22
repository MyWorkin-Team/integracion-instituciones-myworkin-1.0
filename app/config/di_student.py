from app.infrastructure.firebase.firebase_client import init_firebase
from app.infrastructure.firebase.student_repository_adapter import StudentRepositoryAdapter
from app.application.student.register_student_use_case import RegisterStudentUseCase
from app.application.student.update_student_use_case import UpdateStudentByCoIdPsUseCase
from app.application.student.get_student_by_id_use_case import GetStudentByIdUseCase
from fastapi import Path
from fastapi.params import Depends

def get_firebase_app(university_id: str = Path(...)):
    """Inyecta la Firebase App completa (ulima, utrujillo, etc.)"""
    # Esta función llama a tu init_firebase(university_id) modificado
    return init_firebase(university_id)

def get_student_repo(app = Depends(get_firebase_app)):
    """Inyecta el repositorio pasándole la APP completa"""
    return StudentRepositoryAdapter(app)

# Los casos de uso se mantienen igual, pero ahora reciben un repo que 'conoce' su App
def register_student_use_case(repo = Depends(get_student_repo)):
    return RegisterStudentUseCase(repo)

def update_by_co_id_ps_use_case(repo = Depends(get_student_repo)):
    return UpdateStudentByCoIdPsUseCase(repo)

def get_student_by_id_use_case(repo = Depends(get_student_repo)):
    return GetStudentByIdUseCase(repo)

# 2. ¿Qué pasa con repo_use_case?
# Ya no puede ser una función que llamas manualmente. 
# Si la necesitas en un router, úsala así:
def get_repo_di(repo = Depends(get_student_repo)):
    return repo