from datetime import datetime, timezone
from app.domain.model.company import Company
from app.domain.port.company_repository_port import CompanyRepositoryPort
from app.infrastructure.firebase.firebase_client import create_firebase_user, set_firebase_user_claims, get_firebase_user_by_email
from app.infrastructure.firebase.firebase_exceptions import FirebaseUserAlreadyExists

from app.application.company.company_exceptions import CompanyUserEmailAlreadyExists

class UpsertCompanyUseCase:
    def __init__(self, repo: CompanyRepositoryPort):
        self.repo = repo

    def execute(self, company: Company):
        now = datetime.now(timezone.utc)

        # 1. Intentar buscar por RUC
        existing = self.repo.find_by_ruc(company.ruc)

        # Validar que al crear, debe haber al mínimo un usuario con rol "ceo"
        if not existing:
            if not company.users_companies or len(company.users_companies) == 0:
                raise ValueError("Al crear una empresa, debe proporcionar al menos un usuario con rol 'owner' en users_companies")

            owner_exists = any(user.get("role") == "owner" for user in company.users_companies)
            if not owner_exists:
                raise ValueError("Al crear una empresa, debe haber al menos un usuario con rol 'owner'")

        if existing:
            # 2. Si existe, actualizar
            company.id = existing.get("id")
            company.updatedAt = now
            # Mantener el createdAt original si existe en el doc de Firestore
            company.createdAt = existing.get("createdAt")

            self.repo.update_by_ruc(company.ruc, company.to_firestore_dict())
            owner_uid, roles = self._save_relations(company)

            # Si existe un owner, actualizar la company con su UID y roles
            if owner_uid or roles:
                update_data = {}
                if owner_uid:
                    update_data["ownerId"] = owner_uid
                if roles:
                    update_data["roles"] = roles
                self.repo.update_by_ruc(company.ruc, update_data)

            return "updated"
        
        # 3. Si no existe, crear
        company.createdAt = now
        company.updatedAt = now

        company_id = self.repo.save(company)
        company.id = company_id

        owner_uid, roles = self._save_relations(company)

        # Si existe un owner, actualizar la company con su UID y roles
        if owner_uid or roles:
            update_data = {}
            if owner_uid:
                update_data["ownerId"] = owner_uid
            if roles:
                update_data["roles"] = roles
            self.repo.update_by_ruc(company.ruc, update_data)

        return "created"

    def _save_relations(self, company: Company):
        owner_uid = None
        roles = {}
        if company.users_companies:
            for relation in company.users_companies:
                email = relation.get("email")
                if not email:
                    continue

                # 1. Verificar si existe en Firebase Auth (Global)
                try:
                    auth_user = get_firebase_user_by_email(self.repo.app, email)

                    if auth_user:
                        uid = auth_user.uid
                        # 2. Si existe en Auth, verificar si ya tiene relación con esta empresa
                        existing_rel = self.repo.find_user_company_by_email(email)

                        # Si no hay relación previa o es de OTRA empresa: BLOQUEAR
                        # (Si ya existe en el Auth, pero no está en users_companies para esta empresa,
                        # es porque es un estudiante u otro usuario de empresa ajeno).
                        if not existing_rel or existing_rel.get("companyId") != company.id:
                            raise CompanyUserEmailAlreadyExists(email)

                        # Si existe y es la misma empresa, procedemos (será un update)
                        relation["uid"] = uid
                    else:
                        # 3. Si no existe en Auth, crear nuevo
                        uid = self.repo.get_next_user_company_id()
                        default_password = "password123"

                        create_firebase_user(
                            app=self.repo.app,
                            uid=uid,
                            email=email,
                            password=default_password,
                            display_name=email.split('@')[0]
                        )

                        set_firebase_user_claims(
                            app=self.repo.app,
                            uid=uid,
                            claims={"userType": "company"}
                        )

                        relation["uid"] = uid

                except CompanyUserEmailAlreadyExists:
                    raise
                except Exception as e:
                    print(f"Error procesando usuario {email}: {e}")
                    raise

                # Asegurar que el companyId sea el ID de la empresa
                relation["companyId"] = company.id
                self.repo.save_user_company_relation(relation)

                # Agregar rol al diccionario de roles
                user_uid = relation.get("uid")
                user_role = relation.get("role")
                if user_uid and user_role:
                    roles[user_uid] = user_role

                # Si este usuario es owner, guardar su UID
                if user_role == "owner":
                    owner_uid = user_uid

        return owner_uid, roles
