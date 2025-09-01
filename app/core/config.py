import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 기본 설정
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Board API")
    VERSION: str = os.getenv("VERSION", "1.0.0")

    API_PATH: str = os.getenv("API_PATH", "/api/v1")

    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))

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
    # JWT 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings()
