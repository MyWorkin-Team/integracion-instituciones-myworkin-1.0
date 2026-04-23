from datetime import datetime, timezone
import logging
from app.domain.model.company import Company
from app.domain.port.company_repository_port import CompanyRepositoryPort
from app.infrastructure.firebase.firebase_client import create_firebase_user, set_firebase_user_claims, get_firebase_user_by_email, update_firebase_auth_user
from app.infrastructure.firebase.firebase_exceptions import FirebaseUserAlreadyExists

from app.application.company.company_exceptions import CompanyUserEmailAlreadyExists

logger = logging.getLogger(__name__)

class UpsertCompanyUseCase:
    def __init__(self, repo: CompanyRepositoryPort):
        self.repo = repo

    def execute(self, company: Company):
        now = datetime.now(timezone.utc)

        # 1. Intentar buscar por RUC
        existing = self.repo.find_by_ruc(company.ruc)

        if existing:
            # 2. Si existe, actualizar
            company.id = existing.get("id")
            company.updatedAt = now
            # Mantener el createdAt original si existe en el doc de Firestore
            company.createdAt = existing.get("createdAt")

            self.repo.update_by_ruc(company.ruc, company.to_firestore_dict())

            # Actualizar email del owner si cambió
            if company.email:
                existing_owner = self.repo.find_user_company_by_email_and_role(company.id, "owner")
                if existing_owner:
                    old_email = existing_owner.get('email')
                    logger.info(f"Actualizando email del owner de {old_email} a {company.email}")
                    existing_owner_id = existing_owner.get("id")
                    owner_uid = existing_owner.get("uid")

                    # Actualizar en users_companies
                    if existing_owner_id:
                        self.repo.update_user_company_email(existing_owner_id, company.email)

                    # Actualizar en Firebase Auth
                    if owner_uid and old_email != company.email:
                        try:
                            logger.info(f"Actualizando email en Firebase Auth para UID {owner_uid}")
                            update_firebase_auth_user(
                                app=self.repo.app,
                                uid=owner_uid,
                                email=company.email
                            )
                            logger.info(f"Email en Firebase Auth actualizado exitosamente")
                        except Exception as e:
                            logger.error(f"Error actualizando email en Firebase Auth: {str(e)}", exc_info=True)

            owner_uid, roles = self._save_relations(company)

            # Si existe un owner, actualizar la company con su UID
            if owner_uid:
                self.repo.update_by_ruc(company.ruc, {"ownerId": owner_uid})

            # Mezclar roles nuevos con existentes
            if roles:
                self.repo.merge_roles_by_ruc(company.ruc, roles)

            return "updated"
        
        # 3. Si no existe, crear
        company.createdAt = now
        company.updatedAt = now

        company_id = self.repo.save(company)
        company.id = company_id

        # Crear automáticamente un users_company con el email de la empresa y rol owner
        if company.email:
            logger.info(f"Creando users_company automático para {company.email}")
            owner_relation = {
                "email": company.email,
                "role": "owner",
                "status": "active",
                "companyId": company.id,
                "forcePasswordChangeOnNextLogin": True,
            }
            try:
                auth_user = get_firebase_user_by_email(self.repo.app, company.email)
                if auth_user:
                    logger.info(f"Usuario {company.email} ya existe en Firebase Auth con UID {auth_user.uid}")
                    owner_relation["uid"] = auth_user.uid
                else:
                    # Crear nuevo usuario en Firebase Auth
                    uid = self.repo.get_next_user_company_id()
                    logger.info(f"Creando nuevo usuario en Firebase Auth con UID {uid} para {company.email}")
                    default_password = company.ruc
                    create_firebase_user(
                        app=self.repo.app,
                        uid=uid,
                        email=company.email,
                        password=default_password,
                        display_name=company.displayName
                    )
                    set_firebase_user_claims(
                        app=self.repo.app,
                        uid=uid,
                        claims={"userType": "company"}
                    )
                    owner_relation["uid"] = uid
                    logger.info(f"Usuario creado exitosamente con UID {uid}")

                logger.info(f"Guardando users_company: {owner_relation}")
                self.repo.save_user_company_relation(owner_relation)
                logger.info(f"users_company guardado exitosamente")

                # Actualizar company con ownerId y roles
                if owner_relation.get("uid"):
                    logger.info(f"Actualizando company {company.ruc} con ownerId {owner_relation['uid']}")
                    self.repo.update_by_ruc(company.ruc, {
                        "ownerId": owner_relation["uid"],
                        "roles": {owner_relation["uid"]: "owner"}
                    })
            except Exception as e:
                logger.error(f"Error creando owner automático para empresa {company.ruc}: {str(e)}", exc_info=True)

        owner_uid, roles = self._save_relations(company)

        # Si hay usuarios adicionales, mezclar roles
        if roles:
            self.repo.merge_roles_by_ruc(company.ruc, roles)

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
                        default_password = relation.get("password") or company.ruc

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
                        # Solo al crear nuevo usuario, forzar cambio de contraseña
                        relation["forcePasswordChangeOnNextLogin"] = True

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
