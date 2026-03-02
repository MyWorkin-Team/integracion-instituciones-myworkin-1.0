import os
from dotenv import load_dotenv

# 🔥 CARGAR .env
load_dotenv()

def parse_list(value: str | None):
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]

import json

# 🔐 API KEYS POR UNIVERSIDAD
def load_university_keys():
    try:
        keys_raw = os.getenv("UNIVERSITY_API_KEYS", "{}")
        return json.loads(keys_raw)
    except Exception as e:
        print(f"Error loading UNIVERSITY_API_KEYS: {e}")
        return {}

UNIVERSITY_API_KEYS = load_university_keys()

# 🔒 Rutas protegidas (Middlewares)
PROTECTED_PATHS = tuple(parse_list(os.getenv("PROTECTED_PATHS")))

