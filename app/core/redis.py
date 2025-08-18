import redis
from app.core.config import settings

# Redis 클라이언트 (세션 저장 및 캐싱용)
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,  # 문자열 자동 디코딩
    health_check_interval=30  # 30초마다 연결 상태 확인
)
