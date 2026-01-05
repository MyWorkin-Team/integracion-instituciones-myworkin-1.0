from app.domain.model.employer import Employer
from app.delivery.schemas.employer_ulima_dto import EmployerULimaDTO


def ulima_employer_to_domain(body: EmployerULimaDTO) -> Employer:
    data = body.model_dump(exclude_unset=True)

    return Employer(
        id=data.get("id"),
        label=data.get("label"),
        name=data.get("name"),
        alias=data.get("alias"),
        importedId=data.get("importedId"),
        taxId=data.get("taxId"),
        description=data.get("description"),
        overview=data.get("overview"),
        website=str(data["website"]) if data.get("website") else None,
        industries=data.get("industries"),
        primaryContact=data.get("primaryContact"),
        accountManager=data.get("accountManager"),
        parent=data.get("parent"),
        address=data.get("address"),
        lastModified=data.get("lastModified"),
    )
