from slowapi import Limiter
from slowapi.util import get_remote_address

# Limiter global único
limiter = Limiter(key_func=get_remote_address)
