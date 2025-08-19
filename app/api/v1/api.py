from fastapi import APIRouter

from app.api.v1.endpoints import auth, board, post

api_v1 = APIRouter()

api_v1.include_router(auth.router, prefix="/auth", tags=["auth"])
api_v1.include_router(board.router, prefix="/boards", tags=["boards"])
api_v1.include_router(post.router, tags=["posts"])
