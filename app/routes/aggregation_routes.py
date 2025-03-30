from fastapi import APIRouter, HTTPException, Body, Query, Depends
from typing import List, Dict, Any, Optional
from app.config.database import get_collection
from app.main import MongoRequest, parse_json
from app.services.mongo_service import MongoService
from app.auth.auth import verify_token, require_admin, Role

router = APIRouter()

# Operaciones de lectura para agregaciones (disponibles para todos)
@router.post("/aggregate")
async def aggregate(
    request: MongoRequest,
    pipeline: List[Dict[str, Any]] = Body(...),
    role: Role = Depends(verify_token)
):
    """Ejecuta una operación de agregación en una colección."""
    try:
        collection = get_collection(request.database, request.collection)
        service = MongoService(collection)
        result = await service.aggregate(pipeline)
        return parse_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/distinct")
async def distinct(
    request: MongoRequest,
    field: str = Body(...),
    filter: Dict[str, Any] = Body(default=None),
    role: Role = Depends(verify_token)
):
    """Encuentra valores únicos para un campo específico."""
    try:
        collection = get_collection(request.database, request.collection)
        service = MongoService(collection)
        result = await service.distinct(field, filter)
        return parse_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Operaciones de modificación para agregaciones (requieren rol de administrador)
@router.post("/group", dependencies=[Depends(require_admin)])
async def group(
    request: MongoRequest,
    key: Dict[str, Any] = Body(...),
    condition: Dict[str, Any] = Body(default={}),
    initial: Dict[str, Any] = Body(...),
    reduce: str = Body(...),
    finalize: str = Body(default=None)
):
    """Realiza una operación de group (agrupación) en una colección. Requiere rol de administrador."""
    try:
        collection = get_collection(request.database, request.collection)
        
        # Convertir código JavaScript en cadenas a funciones JavaScript
        reduce_func = reduce
        finalize_func = finalize
        
        result = collection.group(key, condition, initial, reduce_func, finalize_func)
        return parse_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/map-reduce", dependencies=[Depends(require_admin)])
async def map_reduce(
    request: MongoRequest,
    map_function: str = Body(...),
    reduce_function: str = Body(...),
    out: Dict[str, Any] = Body(...),
    query: Dict[str, Any] = Body(default=None),
    sort: Dict[str, int] = Body(default=None),
    limit: int = Body(default=0),
    finalize: str = Body(default=None)
):
    """Realiza una operación de map-reduce en una colección. Requiere rol de administrador."""
    try:
        collection = get_collection(request.database, request.collection)
        
        result = collection.map_reduce(
            map_function,
            reduce_function,
            out,
            query=query,
            sort=sort,
            limit=limit,
            finalize=finalize
        )
        
        # Si el resultado es una colección, devolver los documentos
        if isinstance(result, dict) and "result" in result:
            out_collection_name = result["result"]
            out_collection = get_collection(request.database, out_collection_name)
            documents = list(out_collection.find())
            return parse_json(documents)
        
        return parse_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", dependencies=[Depends(require_admin)])
async def bulk_operations(
    request: MongoRequest,
    operations: List[Dict[str, Any]] = Body(...),
    ordered: bool = Body(default=True)
):
    """Ejecuta operaciones de escritura masiva en una colección. Requiere rol de administrador."""
    try:
        from pymongo import InsertOne, UpdateOne, UpdateMany, ReplaceOne, DeleteOne, DeleteMany
        
        collection = get_collection(request.database, request.collection)
        service = MongoService(collection)
        
        # Convertir operaciones JSON a operaciones pymongo
        bulk_operations = []
        for op in operations:
            op_type = op["type"]
            if op_type == "insert":
                bulk_operations.append(InsertOne(op["document"]))
            elif op_type == "update_one":
                bulk_operations.append(UpdateOne(op["filter"], op["update"], upsert=op.get("upsert", False)))
            elif op_type == "update_many":
                bulk_operations.append(UpdateMany(op["filter"], op["update"], upsert=op.get("upsert", False)))
            elif op_type == "replace_one":
                bulk_operations.append(ReplaceOne(op["filter"], op["replacement"], upsert=op.get("upsert", False)))
            elif op_type == "delete_one":
                bulk_operations.append(DeleteOne(op["filter"]))
            elif op_type == "delete_many":
                bulk_operations.append(DeleteMany(op["filter"]))
            else:
                raise HTTPException(status_code=400, detail=f"Tipo de operación desconocido: {op_type}")
        
        result = await service.bulk_write(bulk_operations, ordered)
        
        # Convertir resultado a un formato JSON serializable
        return {
            "inserted_count": result.inserted_count,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "deleted_count": result.deleted_count,
            "upserted_count": result.upserted_count,
            "upserted_ids": [str(id) for id in result.upserted_ids.values()] if result.upserted_ids else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 