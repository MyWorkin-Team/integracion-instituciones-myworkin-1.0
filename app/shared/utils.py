from datetime import datetime
from google.api_core.datetime_helpers import DatetimeWithNanoseconds

def serialize_firestore(value):
    if isinstance(value, DatetimeWithNanoseconds):
        return value.isoformat()

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {k: serialize_firestore(v) for k, v in value.items()}

    if isinstance(value, list):
        return [serialize_firestore(v) for v in value]

    return value
