from datetime import timezone, datetime

def utc_now():
    return datetime.now(timezone.utc)