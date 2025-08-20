import redis
import json
import logging

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from app.core.config import settings

redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    health_check_interval=30,
)
if not redis_client.ping():
    logging.error("Redis server is not reachable")
    raise ConnectionError("Redis server is not reachable")

def create_session(user_id: int, access_token: str, user_info: Dict[str, Any]) -> str:
    session_key = f"session:{user_id}"
    session_data = {
        "user_id": user_id,
        "access_token": access_token,
        "user_info": user_info,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expired": (datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )).isoformat(),
    }
    redis_client.set(
        session_key,
        json.dumps(session_data, ensure_ascii=False),
        ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return session_key

def _get_session(user_id: int) -> Optional[Dict[str, Any]]:
    session_key = f"session:{user_id}"
    raw = redis_client.get(session_key)
    return json.loads(raw) if raw else None

def validate_session(user_id: int, access_token: str) -> bool:
    session_data = _get_session(user_id)
    if not session_data:
        return False
    
    if session_data.get("access_token") != access_token:
        return False

    expired_str = session_data.get("expired")
    if not expired_str:
        delete_session(user_id)
        return False

    expired = datetime.fromisoformat(expired_str)
    if datetime.now(timezone.utc) > expired:
        delete_session(user_id)
        return False

    return True

def delete_session(user_id: int) -> bool:
    session_key = f"session:{user_id}"
    result = redis_client.delete(session_key)
    return result > 0