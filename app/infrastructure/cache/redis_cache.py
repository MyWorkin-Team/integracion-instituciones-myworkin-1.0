import json
from datetime import timedelta
from app.infrastructure.queue.redis_client import get_redis_connection


class RedisCache:
    """Redis cache for validation and deduplication"""

    # Key prefixes
    STUDENT_DNI_PREFIX = "student:dni:"
    STUDENT_EMAIL_PREFIX = "student:email:"
    COMPANY_RUC_PREFIX = "company:ruc:"
    COMPANY_EMAIL_PREFIX = "company:email:"

    # TTL: 24 horas
    DEFAULT_TTL = 86400

    @staticmethod
    def is_dni_registered(dni: str, university_id: str) -> bool:
        """Check if DNI already exists for university"""
        conn = get_redis_connection()
        key = f"{RedisCache.STUDENT_DNI_PREFIX}{university_id}:{dni}"
        return conn.exists(key) > 0

    @staticmethod
    def is_email_registered(email: str, university_id: str, entity_type: str = "student") -> bool:
        """Check if email already exists for university"""
        conn = get_redis_connection()
        prefix = RedisCache.STUDENT_EMAIL_PREFIX if entity_type == "student" else RedisCache.COMPANY_EMAIL_PREFIX
        key = f"{prefix}{university_id}:{email.lower()}"
        return conn.exists(key) > 0

    @staticmethod
    def is_ruc_registered(ruc: str, university_id: str) -> bool:
        """Check if RUC already exists for university"""
        conn = get_redis_connection()
        key = f"{RedisCache.COMPANY_RUC_PREFIX}{university_id}:{ruc}"
        return conn.exists(key) > 0

    @staticmethod
    def register_student(dni: str, email: str, university_id: str):
        """Register student in cache"""
        conn = get_redis_connection()
        dni_key = f"{RedisCache.STUDENT_DNI_PREFIX}{university_id}:{dni}"
        email_key = f"{RedisCache.STUDENT_EMAIL_PREFIX}{university_id}:{email.lower()}"

        conn.setex(dni_key, RedisCache.DEFAULT_TTL, "1")
        conn.setex(email_key, RedisCache.DEFAULT_TTL, "1")

    @staticmethod
    def register_company(ruc: str, email: str, university_id: str):
        """Register company in cache"""
        conn = get_redis_connection()
        ruc_key = f"{RedisCache.COMPANY_RUC_PREFIX}{university_id}:{ruc}"
        email_key = f"{RedisCache.COMPANY_EMAIL_PREFIX}{university_id}:{email.lower()}"

        conn.setex(ruc_key, RedisCache.DEFAULT_TTL, "1")
        if email:
            conn.setex(email_key, RedisCache.DEFAULT_TTL, "1")

    @staticmethod
    def clear_cache(university_id: str = None):
        """Clear all cache or for specific university"""
        conn = get_redis_connection()
        if university_id:
            # Clear for specific university
            patterns = [
                f"{RedisCache.STUDENT_DNI_PREFIX}{university_id}:*",
                f"{RedisCache.STUDENT_EMAIL_PREFIX}{university_id}:*",
                f"{RedisCache.COMPANY_RUC_PREFIX}{university_id}:*",
                f"{RedisCache.COMPANY_EMAIL_PREFIX}{university_id}:*",
            ]
            for pattern in patterns:
                for key in conn.scan_iter(match=pattern):
                    conn.delete(key)
        else:
            # Clear all validation cache
            patterns = [
                f"{RedisCache.STUDENT_DNI_PREFIX}*",
                f"{RedisCache.STUDENT_EMAIL_PREFIX}*",
                f"{RedisCache.COMPANY_RUC_PREFIX}*",
                f"{RedisCache.COMPANY_EMAIL_PREFIX}*",
            ]
            for pattern in patterns:
                for key in conn.scan_iter(match=pattern):
                    conn.delete(key)
