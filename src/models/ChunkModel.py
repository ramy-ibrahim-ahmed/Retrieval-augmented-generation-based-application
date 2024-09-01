from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums import DatabaseEnum
from bson import ObjectId
from pymongo import InsertOne


# Chunck model to manage project collection.
class ChunkModel(BaseDataModel):

    # Get collection:
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_CHUNK_NAME.value]

    # Third party create collection then Indexing:
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    # Apply indexes:
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DatabaseEnum.COLLECTION_CHUNK_NAME not in all_collections:
            self.collection = self.db_client[DatabaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    keys=index["key"],
                    name=index["name"],
                    unique=index["unique"],
                )

    # Create chunk:
    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(
            chunk.model_dump(by_alias=True, exclude_unset=True)
        )
        chunk._id = result.inserted_id
        return chunk

    # Search for chunk with its ID:
    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if result is None:
            return None
        return DataChunk(**result)

    # Insert chunks in database:
    # when write chunks on database write it chunk by chunk?
    # it is not memory efficent so we need "bulk write | batch write".
    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
        chunks_count = 0
        for i in range(0, len(chunks), batch_size):
            # 1. get batch of chunks
            # 2. insert batch of cunks as bulk write
            # 3. return how many chunks inserted
            batch = chunks[i : i + batch_size]
            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]
            await self.collection.bulk_write(operations)
            chunks_count += len(operations)
        return chunks_count

    # if reset delete chunks by project_id & return count deleted.
    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count
