from app.domain.model.company import Company
from app.domain.port.company_repository_port import CompanyRepositoryPort

class UpsertCompanyUseCase:
    def __init__(self, repo: CompanyRepositoryPort):
        self.repo = repo

    def execute(self, company: Company):
        # 1. Intentar buscar por RUC
        existing = self.repo.find_by_ruc(company.ruc)
        
        if existing:
            # 2. Si existe, actualizar
            company.id = existing.get("id")
            self.repo.update_by_ruc(company.ruc, company.to_firestore_dict())
            self._save_relations(company)
            return "updated"
        
        # 3. Si no existe, crear
        if not company.id:
            pass

        self.repo.save(company)
        # Después de salvar, si el repo actualizó el objeto con el ID (o si lo buscamos de nuevo)
        if not company.id:
             new_doc = self.repo.find_by_ruc(company.ruc)
             if new_doc:
                 company.id = new_doc.get("id")

        self._save_relations(company)
        return "created"

    def _save_relations(self, company: Company):
        if company.users_companies:
            for relation in company.users_companies:
                # Asegurar que el companyId sea el ID de la empresa
                relation["companyId"] = company.id
                self.repo.save_user_company_relation(relation)
