import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from enum import Enum
from typing import Optional

# Cargar variables de entorno
load_dotenv()

# Obtener API Key desde variables de entorno
API_KEY = os.getenv("MONGO_API_KEY")

# Definir roles
class Role(str, Enum):
    ADMIN = "admin"
    READER = "reader"

# Configurar esquema de seguridad de Bearer token
security = HTTPBearer(auto_error=False)

# Función para extraer y validar el token
async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Role:
    """
    Verifica el Bearer token y devuelve el rol correspondiente.
    Si no hay token o es inválido, devuelve el rol READER.
    Si el token es válido (coincide con MONGO_API_KEY), devuelve el rol ADMIN.
    """
    if credentials is None:
        return Role.READER
        
    # Verificar si el token coincide con la API Key
    if credentials.scheme.lower() == "bearer" and credentials.credentials == API_KEY:
        return Role.ADMIN
    
    return Role.READER

# Dependencia para requerir rol de administrador
async def require_admin(role: Role = Depends(verify_token)):
    """
    Dependencia que verifica que el usuario tenga el rol de ADMIN.
    Si no es así, lanza una excepción 403 Forbidden.
    """
    if role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere acceso de administrador para esta operación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True 