from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums import DataBaseEnum
from bson import ObjectId


# Asset model to manage assets collection:
class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSET_NAME not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    keys=index["key"],
                    name=index["name"],
                    unique=index["unique"],
                )

    # Create asset:
    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(
            asset.model_dump(by_alias=True, exclude_unset=True)
        )
        asset.id = result.inserted_id
        return asset

    # Get all project assets
    async def get_all_project_assets(self, project_id: str, asset_type: str):
        # 1. convert project id to ObjectId.
        # 2. find all where project by asset_project ID and assset type.
        # 3. where query in list on (length = None)--all records not ex: 5.
        # 4. convert records to pydantic asset inserting them in list.
        project_id = ObjectId(project_id) if isinstance(project_id, str) else project_id
        records = await self.collection.find(
            {
                "asset_project_id": project_id,
                "asset_type": asset_type,
            }
        ).to_list(length=None)
        return [Asset(**record) for record in records]

    # Get all project assets for specified project and file
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        asset_project_id = (
            ObjectId(asset_project_id)
            if isinstance(asset_project_id, str)
            else asset_project_id
        )
        record = await self.collection.find_one(
            {"asset_project_id": asset_project_id, "asset_name": asset_name}
        )
        if record:
            return Asset(**record)
        else:
            return None
