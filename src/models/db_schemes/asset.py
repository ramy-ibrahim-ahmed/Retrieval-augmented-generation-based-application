from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone


# Asset collection for upload asset information in database":
# asset can be any data type.
class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    # asset name is the file id "12alnum + file name + extention".
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)
    # optional config for asset for future usage.
    asset_config: dict = Field(default=None)
    # created asset time.
    asset_pushed_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("asset_project_id", 1),
                ],
                "name": "asset_project_id_index_1",
                "unique": False,
            },
            {
                "key": [
                    ("asset_project_id", 1),
                    ("asset_name", 1),
                ],
                "name": "asset_name_project_id_index_1",
                "unique": True,
            },
        ]
