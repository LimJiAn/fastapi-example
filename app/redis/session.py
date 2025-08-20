import redis
import logging

from app.core.config import settings

redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    health_check_interval=30,
)
if not redis_client.ping():
    logging.error("Redis server is not reachable")
    raise ConnectionError("Redis server is not reachable")