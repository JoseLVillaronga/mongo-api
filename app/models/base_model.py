from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from bson import ObjectId
from datetime import datetime

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source, _handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.string_schema(pattern=r'^[0-9a-f]{24}$', 
                                    to_python=lambda v: ObjectId(v)),
        ])

class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }

    def dict(self, **kwargs):
        kwargs.pop("by_alias", None)
        return super().model_dump(by_alias=True, **kwargs)

    def to_mongo(self):
        """Convierte el modelo a un documento MongoDB"""
        data = self.dict(by_alias=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data 