from fastapi import APIRouter, HTTPException, Body, Query, Path, Depends
from typing import List, Dict, Any, Optional, Union
from app.config.database import get_collection, client
from app.main import MongoRequest, parse_json
from app.services.mongo_service import MongoService
from app.auth.auth import verify_token, require_admin, Role

router = APIRouter()

# Operaciones de lectura para índices (disponibles para todos)
@router.get("/indexes")
async def list_indexes(request: MongoRequest = Depends(), role: Role = Depends(verify_token)):
    """Lista todos los índices de una colección."""
    try:
        collection = get_collection(request.database, request.collection)
        service = MongoService(collection)
        indexes = await service.list_indexes()
        return parse_json(indexes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indexes/analyze")
async def analyze_index_usage(request: MongoRequest = Depends(), role: Role = Depends(verify_token)):
    """Analiza el uso de índices en una colección."""
    try:
        db = client[request.database]
        result = db.command("indexStats", request.collection)
        return parse_json(result)
    except Exception as e:
        # Si el comando no está disponible (solo funciona con MongoDB Enterprise)
        if "no such command" in str(e):
            raise HTTPException(
                status_code=400, 
                detail="El comando indexStats solo está disponible en MongoDB Enterprise"
            )
        raise HTTPException(status_code=500, detail=str(e))

# Operaciones de modificación para índices (requieren rol de administrador)
@router.post("/indexes", dependencies=[Depends(require_admin)])
async def create_index(
    request: MongoRequest,
    keys: Union[str, List[Dict[str, int]]] = Body(...),
    unique: bool = Body(False),
    name: str = Body(None),
    background: bool = Body(True),
    sparse: bool = Body(False),
    expireAfterSeconds: int = Body(None),
    partialFilterExpression: Dict[str, Any] = Body(None)
):
    """Crea un índice en una colección. Requiere rol de administrador."""
    try:
        collection = get_collection(request.database, request.collection)
        service = MongoService(collection)
        
        # Convertir keys a formato de tuplas si es una lista de diccionarios
        if isinstance(keys, list):
            keys_tuples = [(item["field"], item["order"]) for item in keys]
        else:
            keys_tuples = keys
            
        kwargs = {}
        if name:
            kwargs["name"] = name
        if background:
            kwargs["background"] = background
        if sparse:
            kwargs["sparse"] = sparse
        if expireAfterSeconds is not None:
            kwargs["expireAfterSeconds"] = expireAfterSeconds
        if partialFilterExpression:
            kwargs["partialFilterExpression"] = partialFilterExpression
            
        result = await service.create_index(keys_tuples, unique, **kwargs)
        return {"index_name": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/indexes/{index_name}", dependencies=[Depends(require_admin)])
async def drop_index(
    request: MongoRequest = Depends(),
    index_name: str = Path(...)
):
    """Elimina un índice de una colección. Requiere rol de administrador."""
    try:
        collection = get_collection(request.database, request.collection)
        service = MongoService(collection)
        result = await service.drop_index(index_name)
        return parse_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/indexes", dependencies=[Depends(require_admin)])
async def drop_all_indexes(request: MongoRequest = Depends()):
    """Elimina todos los índices de una colección, excepto el índice _id. Requiere rol de administrador."""
    try:
        collection = get_collection(request.database, request.collection)
        collection.drop_indexes()
        return {"message": "Todos los índices han sido eliminados"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 