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

def init_firebase(university_id: str):
    app_name = university_id.lower()

    # 1. Verificar si ya está inicializada
    if app_name in firebase_admin._apps:
        return firebase_admin.get_app(app_name)

    # 2. Obtener credenciales del entorno
    env_var_name = f"FIREBASE_SERVICE_ACCOUNT_{university_id.upper()}"
    service_account_json = os.getenv(env_var_name)

    if not service_account_json:
        logger.error(f"Configuración faltante: {env_var_name}")
        raise RuntimeError(f"La variable {env_var_name} no está configurada")

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
# # ------------------------------------
# # Auth
# # ------------------------------------
# def create_firebase_user(
#     email: str,
#     password: str,
#     display_name: str | None = None
# ):
#     init_firebase()

#     try:
#         user = auth.create_user(
#             email=email,
#             password=password,
#             display_name=display_name,
#             email_verified=False,
#             disabled=False,
#         )

#         return {
#             "uid": user.uid,
#             "email": user.email,
#         }

#     except auth.EmailAlreadyExistsError:
#         raise FirebaseUserAlreadyExists(
#             "El email ya está registrado en Firebase Auth"
#         )

#     except Exception as e:
#         raise FirebaseUserCreateError(str(e))

# # --------------------------------------------------
# # Auth - UPDATE
# # --------------------------------------------------
# def update_firebase_auth_user(
#     uid: str,
#     email: str | None = None,
#     display_name: str | None = None,
# ):
#     """
#     Actualiza email / phone de un usuario en Firebase Auth
#     """
#     init_firebase()

#     try:
#         auth.update_user(
#             uid,
#             email=email,
#             display_name=display_name,
#         )

#     except auth.UserNotFoundError:
#         raise FirebaseUserNotFound("Usuario no existe en Firebase Auth")

#     except Exception as e:
#         raise FirebaseUserUpdateError(str(e))


# # LOCALHOST

# import firebase_admin
# from firebase_admin import credentials, firestore, auth
# from functools import lru_cache


# # @lru_cache
# # def get_firestore():
# #     if not firebase_admin._apps:
# #         cred = credentials.Certificate("serviceAccountKey.json")
# #         firebase_admin.initialize_app(cred)

# #     return firestore.client()


# # class FirebaseUserAlreadyExists(Exception):
# #     pass


# # class FirebaseUserCreateError(Exception):
# #     pass

# class FirebaseError(Exception):
#     """Excepción base para errores Firebase"""
#     pass


# class FirebaseUserNotFound(FirebaseError):
#     pass


# class FirebaseUserAlreadyExists(FirebaseError):
#     pass


# class FirebaseUserCreateError(FirebaseError):
#     pass


# class FirebaseUserUpdateError(FirebaseError):
#     pass


# # def create_firebase_user(email: str, password: str, display_name: str | None = None):
# #     """
# #     Crea un usuario en Firebase Authentication usando Admin SDK
# #     """
# #     # Asegura que Firebase esté inicializado
# #     if not firebase_admin._apps:
# #         cred = credentials.Certificate("serviceAccountKey.json")
# #         firebase_admin.initialize_app(cred)

# #     try:
# #         user = auth.create_user(
# #             email=email,
# #             password=password,
# #             display_name=display_name,
# #             email_verified=False,
# #             disabled=False,
# #         )

# #         return {
# #             "uid": user.uid,
# #             "email": user.email,
# #         }

# #     except auth.EmailAlreadyExistsError:
# #         raise FirebaseUserAlreadyExists("El email ya existe en Firebase Auth")

# #     except Exception as e:
# #         raise FirebaseUserCreateError(str(e))


# # DESPLEGADO

# import os
# import json
# import firebase_admin
# from firebase_admin import credentials, firestore, auth


# def get_firestore():
#     if not firebase_admin._apps:
#         firebase_cred = os.getenv("FIREBASE_SERVICE_ACCOUNT")
#         if not firebase_cred:
#             raise RuntimeError("FIREBASE_SERVICE_ACCOUNT not set")

#         cred_dict = json.loads(firebase_cred)
#         cred = credentials.Certificate(cred_dict)
#         firebase_admin.initialize_app(cred)

#     return firestore.client()


# def create_firebase_user(email: str, password: str, display_name: str | None = None):
#     """
#     Crea un usuario en Firebase Authentication
#     """
#     if not firebase_admin._apps:
#         # Asegura inicialización si solo se usa auth
#         firebase_cred = os.getenv("FIREBASE_SERVICE_ACCOUNT")
#         if not firebase_cred:
#             raise RuntimeError("FIREBASE_SERVICE_ACCOUNT not set")

#         cred_dict = json.loads(firebase_cred)
#         cred = credentials.Certificate(cred_dict)
#         firebase_admin.initialize_app(cred)

#     try:
#         user = auth.create_user(
#             email=email,
#             password=password,
#             display_name=display_name,
#             email_verified=False,
#             disabled=False,
#         )

#         return {
#             "uid": user.uid,
#             "email": user.email,
#         }

#     except auth.EmailAlreadyExistsError:
#         # ✅ CLAVE
#         raise FirebaseUserAlreadyExists(
#             "El email ya está registrado en Firebase Auth"
#         )

#     except Exception as e:
#         raise FirebaseUserCreateError(str(e))
    
