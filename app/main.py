from fastapi import FastAPI, HTTPException, Query, Body, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from bson import ObjectId, json_util
from pydantic import BaseModel
import json
from typing import Callable
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title="MongoDB API Ultra-rápida",
    description="API para interactuar con MongoDB con todas las funcionalidades nativas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Convertidor para convertir objetos BSON a JSON
def parse_json(data):
    return json.loads(json_util.dumps(data))

# Clase para manejar la solicitud de base de datos y colección
class MongoRequest(BaseModel):
    database: str
    collection: str

# Dependencia para validar el ObjectId
def validate_object_id(id: str = Path(...)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    return id

# Importar rutas
from app.routes.collection_routes import router as collection_router
from app.routes.document_routes import router as document_router
from app.routes.aggregation_routes import router as aggregation_router
from app.routes.index_routes import router as index_router

# Incluir routers
app.include_router(collection_router, prefix="/api", tags=["Colecciones"])
app.include_router(document_router, prefix="/api", tags=["Documentos"])
app.include_router(aggregation_router, prefix="/api", tags=["Agregaciones"])
app.include_router(index_router, prefix="/api", tags=["Índices"])

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API Ultra-rápida de MongoDB"} 