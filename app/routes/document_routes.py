from fastapi import APIRouter, HTTPException, Body, Query, Path, Depends, Request
from typing import List, Dict, Any, Optional
from bson import ObjectId
from app.config.database import get_collection
from app.main import MongoRequest, parse_json, validate_object_id
from app.services.mongo_service import MongoService
from app.auth.auth import verify_permission, Role

router = APIRouter()

# READ (Operaciones de lectura disponibles según configuración)
@router.get("/documents/{id}")
async def get_document_by_id(
    request: Request,
    mongo_request: MongoRequest = Depends(),
    id: str = Depends(validate_object_id),
    role: Role = Depends(verify_permission)
):
    """Obtiene un documento por su ID."""
    try:
        collection = get_collection(mongo_request.database, mongo_request.collection)
        service = MongoService(collection)
        document = await service.find_by_id(id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return parse_json(document)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/find")
async def find_documents(
    request: Request,
    mongo_request: MongoRequest,
    filter: Dict[str, Any] = Body(default={}),
    projection: Dict[str, Any] = Body(default=None),
    sort: List[Dict[str, int]] = Body(default=None),
    skip: int = Body(default=0),
    limit: int = Body(default=0),
    role: Role = Depends(verify_permission)
):
    """Encuentra documentos que coincidan con el filtro."""
    try:
        collection = get_collection(mongo_request.database, mongo_request.collection)
        service = MongoService(collection)
        
        # Convertir sort a formato de tuplas si existe
        sort_tuples = None
        if sort:
            sort_tuples = [(item["field"], item["order"]) for item in sort]
            
        documents = await service.find_many(filter, projection, sort_tuples, skip, limit)
        return {"count": len(documents), "documents": parse_json(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/count")
async def count_documents(
    request: Request,
    mongo_request: MongoRequest,
    filter: Dict[str, Any] = Body(default={}),
    role: Role = Depends(verify_permission)
):
    """Cuenta el número de documentos que coinciden con el filtro."""
    try:
        collection = get_collection(mongo_request.database, mongo_request.collection)
        service = MongoService(collection)
        count = await service.count_documents(filter)
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# CREATE, UPDATE, DELETE (Permisos basados en configuración)
@router.post("/documents")
async def insert_document(
    request: Request,
    mongo_request: MongoRequest,
    document: Dict[str, Any] = Body(...),
    role: Role = Depends(verify_permission)
):
    """Inserta un documento en una colección."""
    try:
        collection = get_collection(mongo_request.database, mongo_request.collection)
        service = MongoService(collection)
        result = await service.insert_one(document)
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/many")
async def insert_many_documents(
    request: Request,
    mongo_request: MongoRequest,
    documents: List[Dict[str, Any]] = Body(...),
    role: Role = Depends(verify_permission)
):
    """Inserta múltiples documentos en una colección."""
    try:
        collection = get_collection(mongo_request.database, mongo_request.collection)
        service = MongoService(collection)
        result = await service.insert_many(documents)
        return {"inserted_ids": [str(id) for id in result]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/documents/{id}")
async def update_document_by_id(
    request: Request,
    mongo_request: MongoRequest = Depends(),
    id: str = Depends(validate_object_id),
    update: Dict[str, Any] = Body(...),
    upsert: bool = Query(False),
    role: Role = Depends(verify_permission)
):
    """Actualiza un documento por su ID."""
    try:
        collection = get_collection(mongo_request.database, mongo_request.collection)
        service = MongoService(collection)
        
        # Asegurarse de que update esté en formato de actualización de MongoDB
        if not any(key.startswith('$') for key in update.keys()):
            update = {'$set': update}
            
        result = await service.update_by_id(id, update, upsert)
        if result.matched_count == 0 and not upsert:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
            
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/update")
async def update_documents(
    request: Request,
    mongo_request: MongoRequest,
    filter: Dict[str, Any] = Body(...),
    update: Dict[str, Any] = Body(...),
    upsert: bool = Body(False),
    many: bool = Body(False),
    role: Role = Depends(verify_permission)
):
    """Actualiza uno o varios documentos según el filtro."""
    try:
        collection = get_collection(mongo_request.database, mongo_request.collection)
        service = MongoService(collection)
        
        # Asegurarse de que update esté en formato de actualización de MongoDB
        if not any(key.startswith('$') for key in update.keys()):
            update = {'$set': update}
            
        if many:
            result = await service.update_many(filter, update, upsert)
        else:
            result = await service.update_one(filter, update, upsert)
            
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{id}")
async def delete_document_by_id(
    request: Request,
    mongo_request: MongoRequest = Depends(),
    id: str = Depends(validate_object_id),
    role: Role = Depends(verify_permission)
):
    """Elimina un documento por su ID."""
    try:
        collection = get_collection(mongo_request.database, mongo_request.collection)
        service = MongoService(collection)
        result = await service.delete_by_id(id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return {"deleted_count": result.deleted_count}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/delete")
async def delete_documents(
    request: Request,
    mongo_request: MongoRequest,
    filter: Dict[str, Any] = Body(...),
    many: bool = Body(False),
    role: Role = Depends(verify_permission)
):
    """Elimina uno o varios documentos según el filtro."""
    try:
        collection = get_collection(mongo_request.database, mongo_request.collection)
        service = MongoService(collection)
        
        if many:
            result = await service.delete_many(filter)
        else:
            result = await service.delete_one(filter)
            
        return {"deleted_count": result.deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/find-and-modify")
async def find_and_modify(
    request: Request,
    mongo_request: MongoRequest,
    filter: Dict[str, Any] = Body(...),
    update: Dict[str, Any] = Body(None),
    replacement: Dict[str, Any] = Body(None),
    delete: bool = Body(False),
    return_document: bool = Body(True),
    upsert: bool = Body(False),
    role: Role = Depends(verify_permission)
):
    """Encuentra un documento y lo modifica, reemplaza o elimina según los parámetros."""
    try:
        collection = get_collection(mongo_request.database, mongo_request.collection)
        service = MongoService(collection)
        
        if delete:
            result = await service.find_one_and_delete(filter)
        elif update:
            # Asegurarse de que update esté en formato de actualización de MongoDB
            if not any(key.startswith('$') for key in update.keys()):
                update = {'$set': update}
                
            result = await service.find_one_and_update(
                filter, update, return_document, upsert=upsert
            )
        elif replacement:
            result = await service.find_one_and_replace(
                filter, replacement, return_document, upsert=upsert
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail="Debe proporcionar 'update', 'replacement' o 'delete=true'"
            )
            
        if not result and not upsert:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
            
        return parse_json(result) if result else None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 