from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId


# Project schema:
class Project(BaseModel):
    # key _id automaticlly created within each record in mongo.
    # it is optional because adding it is mongo mission not user.
    # it is object id by motor.

    # because _id starts with "_" pydantic see it as a private.
    # so it doesnt expose it so we need alias.
    # set default None.
    # id for access by pydantic & _id for mongo transactions.
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: str = Field(..., min_length=1)

    # Manual validation in pydantic:
    @field_validator("project_id")
    def validate_project_id(cls, value):
        # value -> its value.
        # project id must be alpha nums.
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric!")
        return value

    # Avoid _id strange datatype, Ignore arbitrary:
    class Config:
        arbitrary_types_allowed = True

    # Index collection by project ID:
    # project_id only key with accending (1) note-decending(-1).
    # unique name for index.
    # unique no redundant for project ID.
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("project_id", 1),
                ],
                "name": "project_id_index_1",
                "unique": True,
            }
        ]
