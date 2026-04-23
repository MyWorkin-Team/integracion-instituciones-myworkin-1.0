import os
from datetime import datetime, timezone
from app.domain.model.student import Student
from app.domain.port.student_repository_port import StudentRepositoryPort
from app.infrastructure.firebase.firebase_client import create_firebase_user, update_firebase_auth_user, set_firebase_user_claims
from app.infrastructure.embedding.generate_degree import generate_degree
from app.shared.utils import generate_search_tokens

class UpsertStudentUseCase:

    def __init__(self, repo: StudentRepositoryPort, university_id: str = None):
        self.repo = repo
        self.university_id = university_id

    def execute(self, student: Student) -> str:
        """
        Realiza un upsert del estudiante:
        1. Busca si ya existe por DNI.
        2. Si existe, actualiza Firestore y Auth.
        3. Si no existe, crea un nuevo usuario en Auth y Firestore.
        Genera el degree si se proporciona una carrera.
        Retorna "created" o "updated".
        """
        existing = self.repo.find_by_dni(student.dni)

        if existing:
            # === UPDATE ===
            firebase_uid = existing.get("uid")
            if not firebase_uid:
                raise RuntimeError("Usuario existe en Firestore pero no tiene firebase_uid")

            # Actualizar Auth
            update_firebase_auth_user(
                app=self.repo.app,
                uid=firebase_uid,
                email=student.email,
                display_name=student.displayName,
            )

            # Actualizar Firestore
            data = student.to_firestore_dict()
            data["updatedAt"] = datetime.now(timezone.utc)
            self.repo.update_by_dni(student.dni, data)
            return "updated"

        else:
            # === CREATE ===
            # Generar ID del documento Firestore
            doc_ref = self.repo.collection.document()
            uid = doc_ref.id

            # Crear usuario en Firebase Auth
            create_firebase_user(
                app=self.repo.app,
                uid=uid,
                email=student.email,
                password=student.cod_student,
                display_name=student.displayName
            )

            # Asignar Custom Claims
            set_firebase_user_claims(
                app=self.repo.app,
                uid=uid,
                claims={"userType": "student"}
            )

            # Preparar datos
            student.uid = uid
            student.createdFrom = 'admin'
            student.createdAt = datetime.now(timezone.utc)
            student.updatedAt = student.createdAt
            student.searchTokens = generate_search_tokens(student.displayName)

            # Guardar en Firestore
            self.repo.save(uid, student)
            return "created"

    def _generate_student_degree(self, career: str, university_id: str = None):
        """Genera el degree para el career del estudiante."""
        try:
            print(f"\n🔍 [DEGREE] Iniciando generación de degree")
            print(f"   → Career: {career}")
            print(f"   → University ID: {university_id}")

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY no configurada")
            print(f"   → GEMINI_API_KEY: {'✅' if api_key else '❌'}")

            # Parsear UNIVERSITY_COUNTRIES
            import json
            countries_json = os.getenv("UNIVERSITY_COUNTRIES", "{}")
            print(f"   → UNIVERSITY_COUNTRIES env: {countries_json}")

            try:
                countries = json.loads(countries_json)
                print(f"   → Parsed countries: {countries}")
            except json.JSONDecodeError:
                countries = {}
                print(f"   → Error parsing UNIVERSITY_COUNTRIES, usando empty dict")

            # Obtener país para la universidad
            country = countries.get(university_id, "").lower()
            if not country:
                raise ValueError(f"País no configurado para universidad: {university_id}")
            print(f"   → Country: {country}")

            # Construir catalogId (myworkin-{country}-{acronym})
            acronym = university_id.lower() if university_id else ""
            catalog_id = f"myworkin-{country}-{acronym}"
            print(f"   → Catalog ID: {catalog_id}")

            # Obtener catálogo desde CORE_COMMONS
            print(f"\n📂 Leyendo catálogo desde CORE_COMMONS...")

            # Inicializar cliente de CORE_COMMONS
            from firebase_admin import credentials, firestore as fb_firestore
            import json

            core_commons_creds = os.getenv("FIREBASE_SERVICE_ACCOUNT_CORE_COMMONS")
            if not core_commons_creds:
                raise ValueError("FIREBASE_SERVICE_ACCOUNT_CORE_COMMONS no configurada")

            print(f"   → FIREBASE_SERVICE_ACCOUNT_CORE_COMMONS: ✅")

            try:
                cred_dict = json.loads(core_commons_creds)
                if "private_key" in cred_dict:
                    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")

                # Usar app de CORE_COMMONS o crear una temporal
                try:
                    from firebase_admin import get_app
                    core_app = get_app("CORE_COMMONS")
                except ValueError:
                    from firebase_admin import initialize_app
                    cred = credentials.Certificate(cred_dict)
                    core_app = initialize_app(cred, name="CORE_COMMONS")

                db = fb_firestore.client(app=core_app)
                print(f"   → Firestore client CORE_COMMONS: {db}")
            except Exception as e:
                print(f"   → Error inicializando CORE_COMMONS: {str(e)}")
                raise

            catalog_doc = db.collection("tenant_config").document(catalog_id).get()
            print(f"   → Documento existe: {catalog_doc.exists}")

            if not catalog_doc.exists:
                raise ValueError(f"Catálogo no encontrado para {catalog_id}")

            catalog_data = catalog_doc.to_dict()
            print(f"   → Catalog data keys: {catalog_data.keys() if catalog_data else 'None'}")

            # Obtener lista de carreras
            careers_list = catalog_data.get("allCareers", [])
            print(f"   → Carreras encontradas: {len(careers_list)}")

            if not careers_list:
                print(f"   → Contenido del documento: {catalog_data}")
                raise ValueError(f"Catálogo vacío para {catalog_id}")

            # Mostrar estructura de la primera carrera
            if careers_list:
                first_career = careers_list[0]
                print(f"   → Estructura de carrera: {first_career.keys() if isinstance(first_career, dict) else type(first_career)}")

            print(f"\n🚀 Generando embedding y buscando coincidencia...")
            degree = generate_degree(career, careers_list, api_key)

            print(f"\n✅ Degree generado exitosamente")
            print(f"   → displayName: {degree.displayName}")
            print(f"   → id: {degree.id}")
            print(f"   → embedding dimensión: {len(degree.embedding)}")
            return degree

        except Exception as e:
            print(f"\n❌ Error generando degree: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
