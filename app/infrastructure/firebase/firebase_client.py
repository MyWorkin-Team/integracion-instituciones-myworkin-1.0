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

def init_firebase():
    if firebase_admin._apps:
        return

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

    if not service_account_json:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON not set")

    cred_dict = json.loads(service_account_json)

    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)


# def init_firebase():
#     if firebase_admin._apps:
#         return

#     # 📍 root del proyecto (donde está app/)
#     project_root = os.getcwd()

#     service_account_path = os.path.join(
#         project_root,
#         "serviceAccountKey.json"
#     )

#     if not os.path.exists(service_account_path):
#         raise RuntimeError(
#             f"Firebase service account not found at {service_account_path}"
#         )

#     cred = credentials.Certificate(service_account_path)
#     firebase_admin.initialize_app(cred)


# ------------------------------------
# Firestore
# ------------------------------------
def get_firestore():
    init_firebase()
    return firestore.client()


# ------------------------------------
# Auth
# ------------------------------------
def create_firebase_user(
    email: str,
    password: str,
    display_name: str | None = None
):
    init_firebase()

    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            email_verified=False,
            disabled=False,
        )

        return {
            "uid": user.uid,
            "email": user.email,
        }

    except auth.EmailAlreadyExistsError:
        raise FirebaseUserAlreadyExists(
            "El email ya está registrado en Firebase Auth"
        )

    except Exception as e:
        raise FirebaseUserCreateError(str(e))

# --------------------------------------------------
# Auth - UPDATE
# --------------------------------------------------
def update_firebase_auth_user(
    uid: str,
    email: str | None = None,
    display_name: str | None = None,
):
    """
    Actualiza email / phone de un usuario en Firebase Auth
    """
    init_firebase()

    try:
        auth.update_user(
            uid,
            email=email,
            display_name=display_name,
        )

    except auth.UserNotFoundError:
        raise FirebaseUserNotFound("Usuario no existe en Firebase Auth")

    except Exception as e:
        raise FirebaseUserUpdateError(str(e))


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
    
