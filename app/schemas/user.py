from uuid import UUID
from typing import Optional
from pydantic import ConfigDict
from fastapi_users import schemas
from app.models.user import UserRole

# Schema para exibir dados do Usuário
class UserRead(schemas.BaseUser[UUID]):
    role: UserRole
    model_config = ConfigDict(from_attributes=True)

# Schema para Criar um Usuário (Cadastro)
class UserCreate(schemas.BaseUserCreate):
    role: UserRole = UserRole.PROFESSOR  # Padrão é Professor

# Schema para Atualizar um Usuário
class UserUpdate(schemas.BaseUserUpdate):
    role: Optional[UserRole] = None