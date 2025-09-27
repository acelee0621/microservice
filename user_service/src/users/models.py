# src/users/models.py
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID
from src.core.models import Base, DateTimeMixin


class User(SQLAlchemyBaseUserTableUUID, Base, DateTimeMixin):
    pass


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass
