# LOCALHOST

import firebase_admin
from firebase_admin import credentials, firestore, auth
from functools import lru_cache


# @lru_cache
# def get_firestore():
#     if not firebase_admin._apps:
#         cred = credentials.Certificate("serviceAccountKey.json")
#         firebase_admin.initialize_app(cred)

#     return firestore.client()


# class FirebaseUserAlreadyExists(Exception):
#     pass


# class FirebaseUserCreateError(Exception):
#     pass

class FirebaseError(Exception):
    """Excepción base para errores Firebase"""
    pass


class FirebaseUserNotFound(FirebaseError):
    pass


class FirebaseUserAlreadyExists(FirebaseError):
    pass


class FirebaseUserCreateError(FirebaseError):
    pass


class FirebaseUserUpdateError(FirebaseError):
    pass


# def create_firebase_user(email: str, password: str, display_name: str | None = None):
#     """
#     Crea un usuario en Firebase Authentication usando Admin SDK
#     """
#     # Asegura que Firebase esté inicializado
#     if not firebase_admin._apps:
#         cred = credentials.Certificate("serviceAccountKey.json")
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
#         raise FirebaseUserAlreadyExists("El email ya existe en Firebase Auth")

#     except Exception as e:
#         raise FirebaseUserCreateError(str(e))


# DESPLEGADO

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth


def get_firestore():
    if not firebase_admin._apps:
        firebase_cred = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if not firebase_cred:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT not set")

        cred_dict = json.loads(firebase_cred)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

    return firestore.client()


def create_firebase_user(email: str, password: str, display_name: str | None = None):
    """
    Crea un usuario en Firebase Authentication
    """
    if not firebase_admin._apps:
        # Asegura inicialización si solo se usa auth
        firebase_cred = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if not firebase_cred:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT not set")

        cred_dict = json.loads(firebase_cred)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

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
        # ✅ CLAVE
        raise FirebaseUserAlreadyExists(
            "El email ya está registrado en Firebase Auth"
        )

    except Exception as e:
        raise FirebaseUserCreateError(str(e))
    

def update_firebase_user(
    uid: str,
    email: str | None = None,
    password: str | None = None,
    display_name: str | None = None,
    disabled: bool | None = None,
):
    """
    Actualiza un usuario en Firebase Authentication
    """
    try:
        user = auth.update_user(
            uid,
            email=email,
            password=password,
            display_name=display_name,
            disabled=disabled,
        )

        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "disabled": user.disabled,
        }

    except auth.UserNotFoundError:
        raise FirebaseUserNotFound("Usuario no existe en Firebase")

    except Exception as e:
        raise FirebaseUserUpdateError(str(e))

def update_firebase_user_by_email(
    email: str,
    **kwargs
):
    """
    Busca el usuario por email y lo actualiza
    """
    try:
        user = auth.get_user_by_email(email)

        return update_firebase_user(
            uid=user.uid,
            **kwargs
        )

    except auth.UserNotFoundError:
        raise FirebaseUserNotFound("Usuario no existe en Firebase")
