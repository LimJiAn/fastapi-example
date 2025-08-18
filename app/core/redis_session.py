import redis.asyncio as redis
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from app.core.config import settings


class RedisSession:
    """Redis를 사용한 세션 관리 클래스"""
    
    def __init__(self):
        self.redis_client = None
    
    async def get_client(self) -> redis.Redis:
        """Redis 클라이언트 연결"""
        if not self.redis_client:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis_client
    
    async def close(self):
        """Redis 연결 종료"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    async def create_session(self, user_id: int, access_token: str, user_info: Dict[str, Any]) -> str:
        """세션 생성
        
        Args:
            user_id: 사용자 ID
            access_token: JWT 액세스 토큰
            user_info: 사용자 정보
            
        Returns:
            str: 세션 키
        """
        try:
            client = await self.get_client()
            session_key = f"session:{user_id}"
            
            session_data = {
                "user_id": user_id,
                "access_token": access_token,
                "user_info": user_info,
                "created": datetime.now(timezone.utc).isoformat(),
                "expired": (datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat()
            }
            # Redis에 세션 저장 (만료 시간 설정)
            await client.set(
                session_key,
                json.dumps(session_data, default=str),
                ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            return session_key

        except Exception as e:
            print(f"Redis 세션 생성 실패: {e}")
            raise

    async def get_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """세션 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Optional[Dict[str, Any]]: 세션 데이터 또는 None
        """
        try:
            client = await self.get_client()
            session_key = f"session:{user_id}"
            
            session_data = await client.get(session_key)
            if session_data:
                return json.loads(session_data)
            return None
            
        except Exception as e:
            print(f"Redis 세션 조회 실패: {e}")
            return None
    
    async def validate_session(self, user_id: int, access_token: str) -> bool:
        """세션 유효성 검증
        
        Args:
            user_id: 사용자 ID
            access_token: JWT 액세스 토큰
            
        Returns:
            bool: 세션 유효 여부
        """
        try:
            session_data = await self.get_session(user_id)
            if not session_data:
                return False
            
            # 토큰 일치 확인
            if session_data.get("access_token") != access_token:
                return False
            
            # 만료 시간 확인
            expired_str = session_data.get("expired", "")
            if not expired_str:
                await self.delete_session(user_id)
                return False
                
            expired = datetime.fromisoformat(expired_str)
            if datetime.now(timezone.utc) > expired:
                await self.delete_session(user_id)
                return False
            
            return True
            
        except Exception as e:
            print(f"Redis 세션 검증 실패: {e}")
            return False
    
    async def delete_session(self, user_id: int) -> bool:
        """세션 삭제
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            client = await self.get_client()
            session_key = f"session:{user_id}"
            
            result = await client.delete(session_key)
            return result > 0
            
        except Exception as e:
            print(f"Redis 세션 삭제 실패: {e}")
            return False
    
    async def refresh_session(self, user_id: int) -> bool:
        """세션 만료 시간 연장
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            bool: 연장 성공 여부
        """
        try:
            client = await self.get_client()
            session_key = f"session:{user_id}"
            
            # 세션 존재 확인
            session_data = await self.get_session(user_id)
            if not session_data:
                return False
            
            # 만료 시간 연장
            await client.expire(session_key, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            
            # 세션 데이터의 expired 업데이트
            session_data["expired"] = (datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat()
            await client.set(
                session_key,
                json.dumps(session_data, default=str),
                ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
            return True
            
        except Exception as e:
            print(f"Redis 세션 연장 실패: {e}")
            return False

# 전역 세션 인스턴스
session = RedisSession()
