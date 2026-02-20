import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth
from app.infrastructure.firebase.firebase_exceptions import (
    FirebaseUserAlreadyExists,
    FirebaseUserCreateError,
    FirebaseUserNotFound,
    FirebaseUserUpdateError
)

# ------------------------------------
# Inicialización ÚNICA de Firebase
# ------------------------------------

# DEPLOY

import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import logging

logger = logging.getLogger(__name__)

_service_accounts_cache = {}

def init_firebase(university_id: str):
    app_name = university_id.lower()

    # 1. Verificar si ya está inicializada
    if app_name in firebase_admin._apps:
        return firebase_admin.get_app(app_name)

    # 2. Obtener credenciales del cache o del entorno
    service_account_json = _service_accounts_cache.get(university_id)
    
    if not service_account_json:
        env_var_name = f"FIREBASE_SERVICE_ACCOUNT_{university_id.upper()}"
        service_account_json = os.getenv(env_var_name)
        if service_account_json:
            _service_accounts_cache[university_id] = service_account_json

    if not service_account_json:
        logger.error(f"Configuración faltante para universidad: {university_id}")
        raise RuntimeError(f"La configuración de Firebase para {university_id} no está configurada")

    try:
        cred_dict = json.loads(service_account_json)
        
        # El SDK a veces necesita que los saltos de línea se procesen manualmente
        if "private_key" in cred_dict:
            cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
        
        cred = credentials.Certificate(cred_dict)
        
        logger.info(f"Inicializando Firebase App para: {app_name}")
        return firebase_admin.initialize_app(cred, name=app_name)
        
    except Exception as e:
        logger.error(f"Error al inicializar Firebase para {university_id}: {e}")
        raise

def get_firestore(university_id: str):
    """
    Retorna el cliente de Firestore específico para una universidad.
    """
    app = init_firebase(university_id)
    return firestore.client(app=app)




# ------------------------------------
# Auth - CREATE
# ------------------------------------
def create_firebase_user(
    app,  # <--- APP ya inicializada
    email: str,
    password: str,
    display_name: str | None = None,
    uid: str | None = None,   # 👈 NUEVO
):
    try:
        user = auth.create_user(
            uid=uid,   # 👈 CLAVE: Forzamos UID si existe
            email=email,
            password=password,
            display_name=display_name,
            email_verified=True,
            disabled=False,
            app=app
        )

        return {
            "uid": user.uid,
            "email": user.email,
        }

    except auth.EmailAlreadyExistsError:
        raise FirebaseUserAlreadyExists("El email ya está registrado")
    except auth.UidAlreadyExistsError:
        raise FirebaseUserAlreadyExists("El UID ya existe en Firebase")
    except Exception as e:
        raise FirebaseUserCreateError(str(e))


# --------------------------------------------------
# Auth - UPDATE
# --------------------------------------------------
def update_firebase_auth_user(
    app,  # <--- Recibe la APP
    uid: str,
    email: str | None = None,
    display_name: str | None = None,
):
    try:
        # Usamos auth.update_user especificando la APP
        auth.update_user(
            uid,
            email=email,
            display_name=display_name,
            app=app  # <--- CLAVE: Usa el proyecto correcto
        )
    except auth.UserNotFoundError:
        raise FirebaseUserNotFound("Usuario no existe")
    except Exception as e:
        raise FirebaseUserUpdateError(str(e))

# --------------------------------------------------
# Auth - SET CUSTOM CLAIMS
# --------------------------------------------------
def set_firebase_user_claims(
    app,  # <--- Recibe la APP
    uid: str,
    claims: dict,
):
    """
    Asigna custom claims (por ejemplo userType: 'student') a un usuario.
    """
    try:
        auth.set_custom_user_claims(uid, claims, app=app)
    except auth.UserNotFoundError:
        raise FirebaseUserNotFound("Usuario no existe")
    except Exception as e:
        raise FirebaseUserUpdateError(str(e))
