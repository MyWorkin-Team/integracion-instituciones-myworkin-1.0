from app.infrastructure.firebase.firebase_client import init_firebase
from app.infrastructure.firebase.employer_repository_adapter import EmployerRepositoryAdapter

from app.application.employer.register_employer_use_case import RegisterEmployerUseCase
from app.application.employer.update_employer_use_case import UpdateEmployerByTaxIdUseCase
from app.application.employer.get_employer_by_tax_id_use_case import GetEmployerByTaxIdUseCase
from fastapi import Path
from fastapi.params import Depends

_repos_cache = {}

def get_firebase_app(university_id: str = Path(...)):
    """Inyecta la Firebase App completa (ulima, utrujillo, etc.)"""
    return init_firebase(university_id)

def get_employer_repo(university_id: str = Path(...), app = Depends(get_firebase_app)):
    """Inyecta el repositorio pasándole la APP completa y usando cache"""
    if university_id not in _repos_cache:
        _repos_cache[university_id] = EmployerRepositoryAdapter(app)
    return _repos_cache[university_id]


# -------------------------------------------------
# Use cases
# -------------------------------------------------
def register_employer_use_case(repo = Depends(get_employer_repo)):
    return RegisterEmployerUseCase(repo)


def update_by_tax_id_use_case(repo = Depends(get_employer_repo)):
    return UpdateEmployerByTaxIdUseCase(repo)


def get_employer_by_tax_id_use_case(repo = Depends(get_employer_repo)):
    return GetEmployerByTaxIdUseCase(repo)

