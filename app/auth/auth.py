import os
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from typing import Optional

from app.auth.role_manager import Role, role_manager

# Cargar variables de entorno
load_dotenv()

# Obtener API Key desde variables de entorno
API_KEY = os.getenv("MONGO_API_KEY")

# Configurar esquema de seguridad de Bearer token
security = HTTPBearer(auto_error=False)

# Función para extraer y validar el token
async def verify_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Role:
    """
    Verifica el Bearer token y devuelve el rol correspondiente según la configuración.
    Si no hay token o es inválido, devuelve el rol predeterminado (normalmente READER).
    Si el token es válido (coincide con MONGO_API_KEY), devuelve el rol de administrador.
    """
    if credentials is None:
        # No hay token, asignar rol predeterminado
        return Role(role_manager.default_role)
        
    # Verificar si el token coincide con la API Key
    if credentials.scheme.lower() == "bearer" and credentials.credentials == API_KEY:
        # Token válido, asignar rol de administrador
        return Role(role_manager.admin_role)
    
    # Token inválido, asignar rol predeterminado
    return Role(role_manager.default_role)

# Middleware para verificar permisos basados en roles
async def verify_permission(request: Request, role: Role = Depends(verify_token)):
    """
    Middleware que verifica si el usuario tiene permiso para acceder al endpoint.
    Utiliza el RoleManager para validar los permisos según la configuración.
    """
    role_manager.enforce_permission(request, role)
    return role

# Dependencia para requerir rol específico (para compatibilidad con código existente)
async def require_admin(role: Role = Depends(verify_token)):
    """
    Dependencia que verifica que el usuario tenga el rol de ADMIN o superior.
    Si no es así, lanza una excepción 403 Forbidden.
    """
    if not role_manager.has_permission(role, Role.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Se requiere rol '{Role.ADMIN}' o superior para esta operación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True 