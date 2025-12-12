from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .file_routes import router as file_router
from .model_routes import router as model_router
from .experiment_routes import router as experiment_router
from .lab_routes import router as lab_router

__all__ = [
    'auth_router',
    'user_router',
    'file_router',
    'model_router',
    'experiment_router',
    'lab_router'
]