from datetime import datetime
from app.config.di_company import init_firebase
from app.infrastructure.firebase.company_repository_adapter import (
    CompanyRepositoryAdapter,
)
from app.application.company.upsert_company_use_case import UpsertCompanyUseCase
from app.domain.model.company import Company
from app.infrastructure.cache.redis_cache import RedisCache


def upsert_company_job(university_id: str, company_dict: dict) -> str:
    app = init_firebase(university_id)
    repo = CompanyRepositoryAdapter(app)
    uc = UpsertCompanyUseCase(repo)

    # Handle datetime serialization
    if company_dict.get("createdAt") and isinstance(company_dict["createdAt"], str):
        company_dict["createdAt"] = datetime.fromisoformat(company_dict["createdAt"])
    if company_dict.get("updatedAt") and isinstance(company_dict["updatedAt"], str):
        company_dict["updatedAt"] = datetime.fromisoformat(company_dict["updatedAt"])

    company = Company(**company_dict)
    result = uc.execute(company)

    # Register in cache after successful Firebase write
    company_email = ""
    if company.users_companies and company.users_companies[0].email:
        company_email = company.users_companies[0].email
    RedisCache.register_company(company.ruc, company_email, university_id)

    return result
