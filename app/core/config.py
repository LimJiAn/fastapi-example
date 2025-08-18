import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 데이터베이스 설정
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://developer:devpassword@postgres:5432/developer"
    )
    # Redis 설정
    REDIS_URL: str = os.getenv(
        "REDIS_URL", 
        "redis://redis:6379/0"
    )
    
settings = Settings()
