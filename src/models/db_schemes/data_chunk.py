from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId


# Chunks schema:
class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)

    # logical forign key for conect data chunk with project.
    # DataChunk._id -> project._id
    chunk_project_id: ObjectId
    
    chunk_asset_id: ObjectId

    # Avoid _id strange datatype, Ignore arbitrary:
    class Config:
        arbitrary_types_allowed = True

    # Index collection with chunk_project ID:
    # can be redundant due to fact one to many.
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("chunk_project_id", 1),
                ],
                "name": "chunk_project_id_index_1",
                "unique": False,
            }
        ]
