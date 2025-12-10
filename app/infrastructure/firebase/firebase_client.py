import firebase_admin
from firebase_admin import credentials, firestore
from functools import lru_cache

@lru_cache
def get_firestore():
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()
