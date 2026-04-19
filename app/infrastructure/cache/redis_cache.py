import json
from datetime import timedelta
from app.infrastructure.queue.redis_client import get_redis_connection


class RedisCache:
    """Redis cache for validation and deduplication"""

    # Key prefixes
    STUDENT_PREFIX = "student:"
    COMPANY_PREFIX = "company:"

    # TTL: 24 horas
    DEFAULT_TTL = 86400

    @staticmethod
    def is_email_registered_globally(email: str) -> tuple[bool, str]:
        """Check if email exists globally (any university, any entity type)
        Returns: (exists, entity_type) where entity_type is 'student', 'company', or None
        """
        conn = get_redis_connection()
        email_lower = email.lower()

        # Check student emails globally
        if any(conn.scan_iter(match=f"{RedisCache.STUDENT_PREFIX}*:*:{email_lower}")):
            return True, "student"

        # Check company emails globally
        if any(conn.scan_iter(match=f"{RedisCache.COMPANY_PREFIX}*:*:{email_lower}")):
            return True, "company"

        return False, None

    @staticmethod
    def is_dni_registered(dni: str, university_id: str) -> bool:
        """Check if student DNI already exists for university"""
        conn = get_redis_connection()
        pattern = f"{RedisCache.STUDENT_PREFIX}{university_id}:{dni}:*"
        return any(conn.scan_iter(match=pattern))

    @staticmethod
    def is_ruc_registered(ruc: str, university_id: str) -> bool:
        """Check if RUC already exists for university"""
        conn = get_redis_connection()
        pattern = f"{RedisCache.COMPANY_PREFIX}{university_id}:{ruc}:*"
        return any(conn.scan_iter(match=pattern))

    @staticmethod
    def register_student(dni: str, email: str, university_id: str, student_data: dict = None):
        """Register student in cache with university_id:dni:email format"""
        conn = get_redis_connection()
        email_lower = email.lower() if email else "no-email"

        # Delete all existing keys for this dni (handles email changes)
        for old_key in conn.scan_iter(match=f"{RedisCache.STUDENT_PREFIX}{university_id}:{dni}:*"):
            conn.delete(old_key)

        key = f"{RedisCache.STUDENT_PREFIX}{university_id}:{dni}:{email_lower}"
        conn.setex(key, RedisCache.DEFAULT_TTL, "1")

        if student_data:
            conn.setex(f"{key}:data", RedisCache.DEFAULT_TTL, json.dumps(student_data, default=str))

    @staticmethod
    def register_company(ruc: str, email: str, university_id: str, company_data: dict = None):
        """Register company in cache with university_id:ruc:email format"""
        conn = get_redis_connection()
        email_lower = email.lower() if email else "no-email"

        # Delete all existing keys for this ruc (handles email changes)
        for old_key in conn.scan_iter(match=f"{RedisCache.COMPANY_PREFIX}{university_id}:{ruc}:*"):
            conn.delete(old_key)

        key = f"{RedisCache.COMPANY_PREFIX}{university_id}:{ruc}:{email_lower}"
        conn.setex(key, RedisCache.DEFAULT_TTL, "1")

        if company_data:
            conn.setex(f"{key}:data", RedisCache.DEFAULT_TTL, json.dumps(company_data, default=str))

    @staticmethod
    def clear_cache(university_id: str = None):
        """Clear all cache or for specific university"""
        conn = get_redis_connection()
        if university_id:
            # Clear for specific university
            patterns = [
                f"{RedisCache.STUDENT_PREFIX}{university_id}:*",
                f"{RedisCache.COMPANY_PREFIX}{university_id}:*",
            ]
            for pattern in patterns:
                for key in conn.scan_iter(match=pattern):
                    conn.delete(key)
        else:
            # Clear all validation cache
            patterns = [
                f"{RedisCache.STUDENT_PREFIX}*",
                f"{RedisCache.COMPANY_PREFIX}*",
            ]
            for pattern in patterns:
                for key in conn.scan_iter(match=pattern):
                    conn.delete(key)
