from app.infrastructure.firebase.firebase_client import init_firebase
from app.infrastructure.firebase.company_repository_adapter import CompanyRepositoryAdapter

from app.application.company.upsert_company_use_case import UpsertCompanyUseCase
from app.application.company.get_company_by_tax_id_use_case import GetCompanyByTaxIdUseCase
from fastapi import Path
from fastapi.params import Depends

_repos_cache = {}

def get_firebase_app(university_id: str = Path(...)):
    return init_firebase(university_id)

def get_company_repo(university_id: str = Path(...), app = Depends(get_firebase_app)):
    if university_id not in _repos_cache:
        _repos_cache[university_id] = CompanyRepositoryAdapter(app)
    return _repos_cache[university_id]

# -------------------------------------------------
# Use cases
# -------------------------------------------------

def upsert_company_use_case(repo = Depends(get_company_repo)):
    return UpsertCompanyUseCase(repo)

def get_company_by_ruc_use_case(repo = Depends(get_company_repo)):
    return GetCompanyByTaxIdUseCase(repo)
