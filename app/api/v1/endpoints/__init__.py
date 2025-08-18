from .auth import router as auth_router
from .boards import router as boards_router  
from .posts import router as posts_router

__all__ = ["auth_router", "boards_router", "posts_router"]
