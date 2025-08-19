from fastapi import APIRouter

from app.api.v1.endpoints import auth, board, post

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(board.router, prefix="/boards", tags=["boards"])
api_router.include_router(post.router, prefix="/posts", tags=["posts"])
