import os
import yaml
from enum import Enum
from typing import Dict, List, Optional, Any
from fastapi import Request, HTTPException, status

# Definición de roles como Enum
class Role(str, Enum):
    PUBLIC = "PUBLIC"
    READER = "READER"
    EDITOR = "EDITOR"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"


class RoleManager:
    """
    Administrador de roles y permisos basado en configuración YAML.
    Controla el acceso a los endpoints según los roles configurados.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RoleManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el administrador de roles cargando la configuración."""
        if self._initialized:
            return
            
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                       "config", "roles.yaml")
        self.config = self._load_config()
        self.endpoints_config = self.config.get("endpoints", {})
        self.default_role = self.config.get("default_role", "READER")
        self.admin_role = self.config.get("admin_role", "ADMIN")
        self.roles_hierarchy = self.config.get("roles_hierarchy", {
            "PUBLIC": 0,
            "READER": 10,
            "EDITOR": 20,
            "ADMIN": 30,
            "SUPERADMIN": 40
        })
        self._initialized = True
    
    def _load_config(self) -> Dict:
        """Carga la configuración desde el archivo YAML."""
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error al cargar la configuración de roles: {e}")
            # Configuración por defecto si no se puede cargar el archivo
            return {
                "default_role": "READER",
                "admin_role": "ADMIN",
                "endpoints": {},
                "roles_hierarchy": {
                    "PUBLIC": 0,
                    "READER": 10,
                    "EDITOR": 20,
                    "ADMIN": 30,
                    "SUPERADMIN": 40
                }
            }
    
    def reload_config(self):
        """Recarga la configuración desde el archivo YAML."""
        self.config = self._load_config()
        self.endpoints_config = self.config.get("endpoints", {})
        self.default_role = self.config.get("default_role", "READER")
        self.admin_role = self.config.get("admin_role", "ADMIN")
        self.roles_hierarchy = self.config.get("roles_hierarchy", {
            "PUBLIC": 0,
            "READER": 10,
            "EDITOR": 20,
            "ADMIN": 30,
            "SUPERADMIN": 40
        })
    
    def get_required_role(self, path: str, method: str) -> str:
        """
        Determina el rol requerido para un endpoint específico.
        
        Args:
            path: Ruta del endpoint (por ejemplo, /api/documents)
            method: Método HTTP (GET, POST, etc.)
            
        Returns:
            El rol requerido como cadena (por ejemplo, "READER", "ADMIN")
        """
        # Normalizar el método
        method = method.upper()
        
        # Buscar el endpoint en la configuración
        for category, endpoints in self.endpoints_config.items():
            for endpoint_name, endpoint_config in endpoints.items():
                if endpoint_config.get("path") == path and endpoint_config.get("method") == method:
                    return endpoint_config.get("required_role", self.default_role)
        
        # Si no se encuentra, devolver el rol predeterminado
        return self.default_role
    
    def has_permission(self, user_role: str, required_role: str) -> bool:
        """
        Verifica si un rol tiene permiso para acceder a un recurso.
        
        Args:
            user_role: Rol del usuario
            required_role: Rol requerido para el recurso
            
        Returns:
            True si tiene permiso, False en caso contrario
        """
        user_level = self.roles_hierarchy.get(user_role, 0)
        required_level = self.roles_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def check_permission(self, request: Request, user_role: str) -> bool:
        """
        Verifica si un usuario tiene permiso para acceder a un endpoint.
        
        Args:
            request: Objeto Request de FastAPI
            user_role: Rol del usuario
            
        Returns:
            True si tiene permiso, False en caso contrario
        """
        path = request.url.path
        method = request.method
        
        required_role = self.get_required_role(path, method)
        
        return self.has_permission(user_role, required_role)
    
    def enforce_permission(self, request: Request, user_role: str):
        """
        Verifica el permiso y genera una excepción si no tiene acceso.
        
        Args:
            request: Objeto Request de FastAPI
            user_role: Rol del usuario
            
        Raises:
            HTTPException: Si el usuario no tiene permiso para acceder al endpoint
        """
        if not self.check_permission(request, user_role):
            path = request.url.path
            method = request.method
            required_role = self.get_required_role(path, method)
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos suficientes. Se requiere el rol '{required_role}' o superior."
            )

# Instancia global del administrador de roles
role_manager = RoleManager() 