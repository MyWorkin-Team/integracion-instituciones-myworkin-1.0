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

    # sitio_web: website -> sitio_web
    sitio_web = data.get("sitio_web") or data.get("website")
    if sitio_web:
        sitio_web = str(sitio_web)

    # sector: extraer de industries[0].label si no viene (formato antiguo)
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

    return Company(
        # === IDENTIDAD ===
        company_id=data.get("company_id"),
        displayName=display_name,
        logo=data.get("logo"),
        ruc=ruc,
        importedId=data.get("importedId"),

        # === INFORMACION ===
        description=data.get("description") or data.get("overview"),
        sitio_web=sitio_web,
        contactEmail=contact_email,
        representative=data.get("representative"),
        phone=phone,

        # === CLASIFICACION ===
        sector=sector,
        companySize=data.get("companySize"),
        roles=data.get("roles"),
        status=data.get("status") or "active",
        users_companies=[c.model_dump() for c in body.users_companies] if body.users_companies else None,

        # === RESPONSE ===
        id=data.get("id"),
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
    )
