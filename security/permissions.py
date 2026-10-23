from fastapi import Depends, HTTPException, status

from models.user_model import User, RolEnum
from security.jwt_service import get_current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.rol != RolEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permisos para realizar esta operación. Solo Administradores."
        )
    return current_user

def require_profesor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.rol not in [RolEnum.PROFESOR, RolEnum.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permisos. Se requiere rol de Profesor."
        )
    return current_user