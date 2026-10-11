from fastapi import APIRouter
from app.core import fastapi_users, auth_backend
from app.schemas import UserRead, UserCreate

router = APIRouter()

# Acopla as rotas de Login / Logout 
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["Auth"]
)

# Acopla as rotas de Registro (Cadastro de novos usuários)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"]
)