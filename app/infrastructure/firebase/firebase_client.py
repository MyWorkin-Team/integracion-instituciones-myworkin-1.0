# import firebase_admin
# from firebase_admin import credentials, firestore
# from functools import lru_cache

# @lru_cache
# def get_firestore():
#     if not firebase_admin._apps:
#         cred = credentials.Certificate("serviceAccountKey.json")
#         firebase_admin.initialize_app(cred)
#     return firestore.client()

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from functools import lru_cache

@lru_cache
def get_firestore():
    if not firebase_admin._apps:

        firebase_cred = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if not firebase_cred:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT not set")

        cred_dict = json.loads(firebase_cred)
        cred = credentials.Certificate(cred_dict)

        firebase_admin.initialize_app(cred)

    return firestore.client()
