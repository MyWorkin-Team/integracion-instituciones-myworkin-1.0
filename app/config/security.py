import os

def parse_list(value: str | None):
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]

# 🔐 API KEY
PUSH_API_KEY = os.getenv("PUSH_API_KEY")

# 🌍 IPs permitidas
ALLOWED_IPS = set(parse_list(os.getenv("ALLOWED_IPS")))

# 🔒 Rutas protegidas (prefijos)
PROTECTED_PATHS = tuple(parse_list(os.getenv("PROTECTED_PATHS")))
