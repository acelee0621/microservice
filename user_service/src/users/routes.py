# src/users/routes.py
from src.users.schemas import UserRead, UserCreate, UserUpdate
from src.users.user_manager import auth_backend,fastapi_users

def include_user_routers(app):
    app.include_router(
        fastapi_users.get_auth_router(auth_backend), 
        prefix="/auth/jwt", 
        tags=["auth"]
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )