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

    # Register in cache with full data after successful Firebase write
    company_email = ""
    users_data = []
    owner_uid = None
    roles = {}

    if company.users_companies:
        company_email = company.users_companies[0].get("email", "")
        for user in company.users_companies:
            users_data.append({
                "email": user.get("email"),
                "firstName": user.get("firstName"),
                "lastName": user.get("lastName"),
            })

            # Obtener el UID del usuario owner
            if user.get("role") == "owner":
                owner_uid = user.get("uid")
                if owner_uid:
                    roles[owner_uid] = "owner"

    cache_data = {
        "university_id": university_id,
        "ruc": company.ruc,
        "displayName": company.displayName,
        "sector": company.sector,
        "phone": company.phone,
        "users_companies": users_data,
        "createdAt": str(company.createdAt) if company.createdAt else None,
        "updatedAt": str(company.updatedAt) if company.updatedAt else None,
    }

    if owner_uid:
        cache_data["ownerUid"] = owner_uid
    if roles:
        cache_data["roles"] = roles

    RedisCache.register_company(company.ruc, company_email, university_id, cache_data)

    return result
