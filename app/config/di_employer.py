from app.infrastructure.firebase.firebase_client import get_firestore
from app.infrastructure.firebase.employer_repository_adapter import EmployerRepositoryAdapter

from app.application.employer.register_employer_use_case import RegisterEmployerUseCase
from app.application.employer.update_employer_use_case import UpdateEmployerByTaxIdUseCase
from app.application.employer.get_employer_by_tax_id_use_case import GetEmployerByTaxIdUseCase


# -------------------------------------------------
# Repository
# -------------------------------------------------
def employer_repo():
    return EmployerRepositoryAdapter(get_firestore())


# -------------------------------------------------
# Use cases
# -------------------------------------------------
def register_employer_use_case():
    return RegisterEmployerUseCase(employer_repo())


def update_by_tax_id_use_case():
    return UpdateEmployerByTaxIdUseCase(employer_repo())


def get_employer_by_tax_id_use_case():
    return GetEmployerByTaxIdUseCase(employer_repo())


# (opcional, por simetría con student)
def repo_use_case():
    return employer_repo()
