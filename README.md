# API Ultra-rápida para MongoDB

Esta API proporciona acceso completo a las funcionalidades nativas de MongoDB a través de una interfaz REST. Permite realizar todas las operaciones CRUD, así como operaciones avanzadas como agregaciones, índices y más.

## Requisitos

- Python 3.8+
- MongoDB 4.0+

## Instalación

1. Clonar el repositorio
2. Activar el entorno virtual: `source venv/bin/activate`
3. Instalar dependencias: `pip install -r requirements.txt`

## Configuración

Edita el archivo `.env` para configurar la conexión a MongoDB:

```env
MONGO_USERNAME=user
MONGO_PASSWORD=password
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_API_KEY=9791cd25-b7e1-4059-d26b-397dee7dd442
```

## Ejecución

```bash
python run.py
```

La API estará disponible en `http://localhost:28000`.

## Instalación como Servicio del Sistema

Para instalar la API como un servicio del sistema (systemd) y que se ejecute automáticamente al iniciar el servidor:

1. Asegúrate de estar en el directorio del proyecto
2. Ejecuta el script de instalación:

```bash
sudo ./install.sh
```

El script realizará automáticamente las siguientes acciones:
- Crear el archivo de configuración del servicio
- Configurarlo para ejecutarse con el usuario actual
- Habilitar el inicio automático
- Iniciar el servicio

Una vez instalado, puedes gestionar el servicio con estos comandos:

```bash
# Ver estado del servicio
sudo systemctl status mongo-api.service

# Iniciar el servicio
sudo systemctl start mongo-api.service

# Detener el servicio
sudo systemctl stop mongo-api.service

# Reiniciar el servicio (después de cambios)
sudo systemctl restart mongo-api.service

# Ver logs en tiempo real
sudo journalctl -u mongo-api.service -f
```

## Documentación

La documentación interactiva estará disponible en `http://localhost:28000/docs`.

### Autenticación en la Documentación

Para utilizar la interfaz de documentación con privilegios de administrador:

1. Accede a `http://localhost:28000/docs`
2. Haz clic en el botón verde "Authorize" en la esquina superior derecha
3. En el campo que aparece, introduce: `Bearer 9791cd25-b7e1-4059-d26b-397dee7dd442`
4. Haz clic en "Authorize" y luego en "Close"

Una vez autorizado, podrás probar todos los endpoints, incluyendo aquellos que requieren permisos de administrador.

## Autenticación y Control de Acceso

La API implementa un sistema de autenticación basado en Bearer tokens y control de acceso basado en roles configurable:

### Roles Disponibles

- **PUBLIC**: Acceso sin autenticación para endpoints públicos
- **READER**: Acceso básico de lectura (por defecto sin token)
- **EDITOR**: Puede crear y modificar datos pero no eliminarlos
- **ADMIN**: Acceso completo (con token válido)
- **SUPERADMIN**: Acceso completo más operaciones administrativas especiales

### Sistema de Permisos Configurable

Todos los permisos y roles están configurados en el archivo `config/roles.yaml`. Este archivo permite:

- Definir el rol mínimo requerido para cada endpoint
- Configurar el rol predeterminado para usuarios sin token
- Configurar el rol asignado a usuarios con token válido
- Definir una jerarquía personalizada de roles

Para modificar la configuración de permisos, edita el archivo `config/roles.yaml`. Los cambios se aplican automáticamente sin necesidad de reiniciar la API.

### Autenticación con Bearer Token

Para acceder con un rol privilegiado, incluye el siguiente encabezado en tus peticiones:

```
Authorization: Bearer 9791cd25-b7e1-4059-d26b-397dee7dd442
```

Si no se proporciona un token o es inválido, se asumirá el rol predeterminado (normalmente READER), con acceso limitado según la configuración.

## Endpoints Principales

### Colecciones
- `GET /api/databases` - Listar bases de datos
- `GET /api/collections?database=<db>` - Listar colecciones
- `POST /api/collections` - Crear colección (requiere admin)
- `DELETE /api/collections` - Eliminar colección (requiere admin)

### Documentos
- `POST /api/documents` - Insertar documento (requiere admin)
- `GET /api/documents/{id}` - Obtener documento por ID
- `PUT /api/documents/{id}` - Actualizar documento por ID (requiere admin)
- `DELETE /api/documents/{id}` - Eliminar documento por ID (requiere admin)
- `POST /api/documents/find` - Buscar documentos
- `POST /api/documents/count` - Contar documentos

### Agregaciones
- `POST /api/aggregate` - Ejecutar pipelines de agregación
- `POST /api/distinct` - Obtener valores distintos
- `POST /api/bulk` - Operaciones en lote (requiere admin)

### Índices
- `GET /api/indexes` - Listar índices
- `POST /api/indexes` - Crear índice (requiere admin)
- `DELETE /api/indexes/{index_name}` - Eliminar índice (requiere admin)

## Ejemplo de uso

```bash
# Obtener documentos (sin autenticación - rol lector)
curl -X POST "http://localhost:28000/api/documents/find" \
  -H "Content-Type: application/json" \
  -d '{
    "mongo_request": {
      "database": "test",
      "collection": "usuarios"
    },
    "filter": {"edad": {"$gt": 25}},
    "sort": [{"field": "edad", "order": 1}],
    "limit": 10
  }'

# Insertar un documento (con autenticación - rol admin)
curl -X 'POST' \
  'http://localhost:28000/api/documents' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer 9791cd25-b7e1-4059-d26b-397dee7dd442' \
  -H 'Content-Type: application/json' \
  -d '{
  "mongo_request": {
    "database": "shop",
    "collection": "products"
  },
  "document": {
    "name": "A Book",
    "price": 15,
    "Description": "Halo, Cience Fiction"
  }
}'
```

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles. 
