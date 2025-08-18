from app.db.base_class import Base

# 반드시 모든 모델들을 import 해야 Base.metadata에 등록됨 (Alembic용)
from app.models.user import User
from app.models.board import Board  
from app.models.post import Post