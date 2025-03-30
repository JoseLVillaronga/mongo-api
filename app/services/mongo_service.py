from typing import List, Dict, Any, Optional, Union, TypeVar, Generic
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from pymongo import ASCENDING, DESCENDING

T = TypeVar('T')

class MongoService(Generic[T]):
    def __init__(self, collection: Collection):
        self.collection = collection

    # CREATE
    async def insert_one(self, document: Dict[str, Any]) -> InsertOneResult:
        """Inserta un documento en la colección."""
        return self.collection.insert_one(document)

    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[ObjectId]:
        """Inserta múltiples documentos en la colección."""
        result = self.collection.insert_many(documents)
        return result.inserted_ids

    # READ
    async def find_one(self, filter: Dict[str, Any], projection: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Encuentra un documento que coincida con el filtro."""
        return self.collection.find_one(filter, projection)

    async def find_by_id(self, id: Union[str, ObjectId], projection: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Encuentra un documento por su ID."""
        if isinstance(id, str):
            id = ObjectId(id)
        return self.collection.find_one({"_id": id}, projection)

    async def find_many(self, 
                        filter: Dict[str, Any] = None, 
                        projection: Dict[str, Any] = None,
                        sort: List[tuple] = None,
                        skip: int = 0, 
                        limit: int = 0) -> List[Dict[str, Any]]:
        """Encuentra múltiples documentos que coincidan con el filtro."""
        cursor = self.collection.find(filter or {}, projection)
        
        if sort:
            cursor = cursor.sort(sort)
        
        cursor = cursor.skip(skip)
        
        if limit > 0:
            cursor = cursor.limit(limit)
            
        return list(cursor)

    async def count_documents(self, filter: Dict[str, Any] = None) -> int:
        """Cuenta el número de documentos que coinciden con el filtro."""
        return self.collection.count_documents(filter or {})

    # UPDATE
    async def update_one(self, 
                        filter: Dict[str, Any], 
                        update: Dict[str, Any], 
                        upsert: bool = False) -> UpdateResult:
        """Actualiza un documento que coincida con el filtro."""
        return self.collection.update_one(filter, update, upsert=upsert)

    async def update_by_id(self, 
                          id: Union[str, ObjectId], 
                          update: Dict[str, Any], 
                          upsert: bool = False) -> UpdateResult:
        """Actualiza un documento por su ID."""
        if isinstance(id, str):
            id = ObjectId(id)
        return self.collection.update_one({"_id": id}, update, upsert=upsert)

    async def update_many(self, 
                         filter: Dict[str, Any], 
                         update: Dict[str, Any], 
                         upsert: bool = False) -> UpdateResult:
        """Actualiza múltiples documentos que coincidan con el filtro."""
        return self.collection.update_many(filter, update, upsert=upsert)

    # DELETE
    async def delete_one(self, filter: Dict[str, Any]) -> DeleteResult:
        """Elimina un documento que coincida con el filtro."""
        return self.collection.delete_one(filter)

    async def delete_by_id(self, id: Union[str, ObjectId]) -> DeleteResult:
        """Elimina un documento por su ID."""
        if isinstance(id, str):
            id = ObjectId(id)
        return self.collection.delete_one({"_id": id})

    async def delete_many(self, filter: Dict[str, Any]) -> DeleteResult:
        """Elimina múltiples documentos que coincidan con el filtro."""
        return self.collection.delete_many(filter)

    # AGGREGATE
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ejecuta una operación de agregación en la colección."""
        return list(self.collection.aggregate(pipeline))

    # INDEXES
    async def create_index(self, keys: Union[str, List[tuple]], unique: bool = False, **kwargs) -> str:
        """Crea un índice en la colección."""
        return self.collection.create_index(keys, unique=unique, **kwargs)

    async def drop_index(self, index_name: str) -> Dict[str, Any]:
        """Elimina un índice de la colección."""
        return self.collection.drop_index(index_name)

    async def list_indexes(self) -> List[Dict[str, Any]]:
        """Lista todos los índices de la colección."""
        return list(self.collection.list_indexes())

    # BULK OPERATIONS
    async def bulk_write(self, operations: List[Any], ordered: bool = True) -> Dict[str, Any]:
        """Ejecuta operaciones de escritura masiva."""
        return self.collection.bulk_write(operations, ordered=ordered)

    # DISTINCT
    async def distinct(self, field: str, filter: Dict[str, Any] = None) -> List[Any]:
        """Encuentra valores únicos para un campo específico."""
        return self.collection.distinct(field, filter)

    # FIND ONE AND UPDATE/DELETE/REPLACE
    async def find_one_and_update(self, 
                                 filter: Dict[str, Any], 
                                 update: Dict[str, Any], 
                                 return_document: bool = True, 
                                 **kwargs) -> Optional[Dict[str, Any]]:
        """Encuentra un documento y lo actualiza."""
        from pymongo import ReturnDocument
        return_doc = ReturnDocument.AFTER if return_document else ReturnDocument.BEFORE
        return self.collection.find_one_and_update(filter, update, return_document=return_doc, **kwargs)

    async def find_one_and_delete(self, filter: Dict[str, Any], **kwargs) -> Optional[Dict[str, Any]]:
        """Encuentra un documento y lo elimina."""
        return self.collection.find_one_and_delete(filter, **kwargs)

    async def find_one_and_replace(self, 
                                  filter: Dict[str, Any], 
                                  replacement: Dict[str, Any], 
                                  return_document: bool = True, 
                                  **kwargs) -> Optional[Dict[str, Any]]:
        """Encuentra un documento y lo reemplaza."""
        from pymongo import ReturnDocument
        return_doc = ReturnDocument.AFTER if return_document else ReturnDocument.BEFORE
        return self.collection.find_one_and_replace(filter, replacement, return_document=return_doc, **kwargs) 