import os
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

# Chave secreta para assinar os tokens JWT (em produção, use uma variável de ambiente)
SECRET_KEY = os.getenv("JWT_SECRET", "SUPER_SECRET_KEY_123_ALTERE_ISSO")

# Transporte define como o token transita (no cabeçalho 'Authorization: Bearer <token>')
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    # Token dura 1 hora
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600) 

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)