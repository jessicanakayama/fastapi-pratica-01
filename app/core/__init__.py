from app.core.security import auth_backend
from app.core.users import fastapi_users, current_active_user
from app.core.roles import requer_coordenador, requer_professor, requer_professor_ou_coordenador