from app.domain.model.employer import Employer
from app.delivery.schemas.employer_dto import EmployerDTO


def employer_to_domain(body: EmployerDTO) -> Employer:
    """
    Mapea DTO de empresa a modelo de dominio.
    Soporta tanto formato nuevo (simplificado) como formato antiguo (backward compatibility).
    """
    data = body.model_dump(exclude_unset=True)

    # === BACKWARD COMPATIBILITY ===

    # displayName: usar label o alias si no viene
    display_name = data.get("displayName") or data.get("label") or data.get("alias")

    # sector: extraer de industries[0].label si no viene
    sector = data.get("sector")
    if not sector:
        industries = data.get("industries")
        if industries and len(industries) > 0:
            sector = industries[0].get("label")

    # contactEmail: extraer de primaryContact si no viene
    contact_email = data.get("contactEmail")
    if not contact_email:
        primary_contact = data.get("primaryContact")
        if primary_contact and isinstance(primary_contact, dict):
            contact_email = primary_contact.get("email")

    # phone: extraer de primaryContact si no viene
    phone = data.get("phone")
    if not phone:
        primary_contact = data.get("primaryContact")
        if primary_contact and isinstance(primary_contact, dict):
            phone = primary_contact.get("phone")

    # website: convertir a string si es HttpUrl
    website = data.get("website")
    if website:
        website = str(website)

    return Employer(
        # === IDENTIDAD ===
        name=data.get("name"),
        displayName=display_name,
        logo=data.get("logo"),
        taxId=data.get("taxId"),
        importedId=data.get("importedId"),

        # === INFORMACION ===
        description=data.get("description") or data.get("overview"),
        website=website,
        contactEmail=contact_email,
        phone=phone,

        # === CLASIFICACION ===
        sector=sector,
        companySize=data.get("companySize"),
        status=data.get("status") or "active",

        # === RESPONSE ===
        id=data.get("id"),
        createdAt=data.get("createdAt"),
        updatedAt=data.get("updatedAt"),
    )
