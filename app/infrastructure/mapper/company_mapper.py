from app.domain.model.company import Company
from app.delivery.schemas.company_dto import CompanyDTO


def company_to_domain(body: CompanyDTO) -> Company:
    """
    Mapea DTO de empresa a modelo de dominio.
    Soporta esquema de 'companies' con mapeo de campos antiguos.
    """
    data = body.model_dump(exclude_unset=True)

    # === BACKWARD COMPATIBILITY & MAPPING ===

    # displayName: usar label o alias si no viene
    display_name = data.get("displayName") or data.get("label") or data.get("alias")

    # ruc: taxId -> ruc
    ruc = data.get("ruc") or data.get("taxId")

    # website: website -> website
    website = data.get("website") or data.get("sitio_web")
    if website:
        website = str(website)

    # sector: extraer de industries[0].label si no viene (formato antiguo)
    sector = data.get("sector")
    if not sector:
        industries = data.get("industries")
        if industries and len(industries) > 0:
            sector = industries[0].get("label")

    # email: extraer de primaryContact si no viene
    email_field = data.get("email") or data.get("contactEmail")
    if not email_field:
        primary_contact = data.get("primaryContact")
        if primary_contact and isinstance(primary_contact, dict):
            email_field = primary_contact.get("email")

    # phone: extraer de primaryContact si no viene
    phone = data.get("phone")
    if not phone:
        primary_contact = data.get("primaryContact")
        if primary_contact and isinstance(primary_contact, dict):
            phone = primary_contact.get("phone")

    return Company(
        # === IDENTIDAD ===
        displayName=display_name,
        logotype=data.get("logotype") or data.get("logo"),
        ruc=ruc,
        importedId=data.get("importedId"),

        # === INFORMACION ===
        description=data.get("description") or data.get("overview"),
        website=website,
        email=email_field,
        representative=data.get("representative"),
        phone=phone,

        # === CLASIFICACION ===
        sector=sector,
        companySize=data.get("companySize"),
        roles=data.get("roles"),
        status=data.get("status") or "active",
        users_companies=data.get("users_companies"),

        # === RESPONSE ===
        id=data.get("id"),
        createdAt=data.get("createdAt") or data.get("created_at"),
        updatedAt=data.get("updatedAt") or data.get("updated_at"),
    )
