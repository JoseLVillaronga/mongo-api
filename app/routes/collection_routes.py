from fastapi import APIRouter, HTTPException, Body, Query, Depends
from typing import List, Dict, Any, Optional
from app.config.database import client
from app.main import MongoRequest, parse_json
from app.auth.auth import verify_token, require_admin, Role

router = APIRouter()

# Operaciones de lectura (disponibles para todos)
@router.get("/databases")
async def get_databases(role: Role = Depends(verify_token)):
    """Obtiene la lista de todas las bases de datos."""
    try:
        databases = client.list_database_names()
        return {"databases": databases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections")
async def get_collections(database: str, role: Role = Depends(verify_token)):
    """Obtiene la lista de todas las colecciones en una base de datos."""
    try:
        db = client[database]
        collections = db.list_collection_names()
        return {"database": database, "collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_collection_stats(request: MongoRequest = Depends(), role: Role = Depends(verify_token)):
    """Obtiene estadísticas de una colección."""
    try:
        db = client[request.database]
        stats = db.command("collstats", request.collection)
        return parse_json(stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Operaciones de modificación (requieren rol de administrador)
@router.post("/collections", dependencies=[Depends(require_admin)])
async def create_collection(request: MongoRequest):
    """Crea una nueva colección en una base de datos. Requiere rol de administrador."""
    try:
        db = client[request.database]
        db.create_collection(request.collection)
        return {"message": f"Colección '{request.collection}' creada con éxito en la base de datos '{request.database}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/collections", dependencies=[Depends(require_admin)])
async def drop_collection(request: MongoRequest):
    """Elimina una colección de una base de datos. Requiere rol de administrador."""
    try:
        db = client[request.database]
        db[request.collection].drop()
        return {"message": f"Colección '{request.collection}' eliminada con éxito de la base de datos '{request.database}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rename", dependencies=[Depends(require_admin)])
async def rename_collection(
    request: MongoRequest,
    new_name: str = Body(..., embed=True)
):
    """Renombra una colección. Requiere rol de administrador."""
    try:
        db = client[request.database]
        db[request.collection].rename(new_name)
        return {"message": f"Colección '{request.collection}' renombrada a '{new_name}' con éxito"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 