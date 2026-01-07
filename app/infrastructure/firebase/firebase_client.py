# LOCALHOST

import firebase_admin
from firebase_admin import credentials, firestore, auth
from functools import lru_cache


@lru_cache
def get_firestore():
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)

    return firestore.client()


class FirebaseUserAlreadyExists(Exception):
    pass


class FirebaseUserCreateError(Exception):
    pass


def create_firebase_user(email: str, password: str, display_name: str | None = None):
    """
    Crea un usuario en Firebase Authentication usando Admin SDK
    """
    # Asegura que Firebase esté inicializado
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
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
        raise FirebaseUserAlreadyExists("El email ya existe en Firebase Auth")

    except Exception as e:
        raise FirebaseUserCreateError(str(e))


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