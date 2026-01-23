from app.infrastructure.firebase.firebase_client import init_firebase
from app.infrastructure.firebase.employer_repository_adapter import EmployerRepositoryAdapter

from app.application.employer.register_employer_use_case import RegisterEmployerUseCase
from app.application.employer.update_employer_use_case import UpdateEmployerByTaxIdUseCase
from app.application.employer.get_employer_by_tax_id_use_case import GetEmployerByTaxIdUseCase
from fastapi import Path
from fastapi.params import Depends

def get_firebase_app(university_id: str = Path(...)):
    """Inyecta la Firebase App completa (ulima, utrujillo, etc.)"""
    # Esta función llama a tu init_firebase(university_id) modificado
    return init_firebase(university_id)

def get_employer_repo(app = Depends(get_firebase_app)):
    """Inyecta el repositorio pasándole la APP completa"""
    return EmployerRepositoryAdapter(app)


# -------------------------------------------------
# Use cases
# -------------------------------------------------
def register_employer_use_case(repo = Depends(get_employer_repo)):
    return RegisterEmployerUseCase(repo)


def update_by_tax_id_use_case(repo = Depends(get_employer_repo)):
    return UpdateEmployerByTaxIdUseCase(repo)


def get_employer_by_tax_id_use_case(repo = Depends(get_employer_repo)):
    return GetEmployerByTaxIdUseCase(repo)

