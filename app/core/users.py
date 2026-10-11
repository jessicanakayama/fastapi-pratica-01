from typing import Optional
from uuid import UUID
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.user import User
from app.core.security import auth_backend

# Adaptador de Banco de Dados do FastAPI Users
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

# Gerenciador de Regras de Usuário (Hash, Registro, etc)
class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = "RESET_PASSWORD_SECRET"
    verification_token_secret = "VERIFY_SECRET"

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"Usuário {user.id} foi registrado com sucesso.")

# Gerenciador de usuários fornecido a aplicação a cada requisição HTTP.
def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# Instância principal do FastAPI Users
fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [auth_backend],
)

# Dependência rápida para pegar o usuário logado atual
current_active_user = fastapi_users.current_user(active=True)