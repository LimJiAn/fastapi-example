from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin


class CRUDUser(CRUDBase[User, UserCreate, UserLogin]):
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        stmt = select(User).where(User.email == email)
        result = db.execute(stmt)
        return result.scalars().first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """사용자 생성"""
        db_obj = User(
            fullname=obj_in.fullname,
            email=obj_in.email,
            password=get_password_hash(obj_in.password),
        )
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """사용자 인증"""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    
user = CRUDUser(User)
