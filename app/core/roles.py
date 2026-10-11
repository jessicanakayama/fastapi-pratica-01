from fastapi import Depends, HTTPException, status
from app.models.user import User, UserRole
from app.core.users import current_active_user

class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(current_active_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para executar esta ação."
            )
        return user

# Atalhos úteis para usar nos endpoints
requer_coordenador = RoleChecker([UserRole.COORDENADOR])
requer_professor = RoleChecker([UserRole.PROFESSOR])
requer_professor_ou_coordenador = RoleChecker([UserRole.PROFESSOR, UserRole.COORDENADOR])