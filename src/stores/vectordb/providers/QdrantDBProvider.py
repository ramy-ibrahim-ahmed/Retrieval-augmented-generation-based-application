from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from qdrant_client import models, QdrantClient

import logging


class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_method: str):
        self.clint = None
        self.distance_method = None
        self.db_path = db_path

        self.logger = logging.getLogger(__name__)

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

    def connect(self):
        self.clint = QdrantClient(path=self.db_path)

    def disconnect(self):
        raise NotImplementedError

    def is_collection_exists(self, collection_name):
        try:
            return self.clint.collection_exists(collection_name=collection_name)

        except Exception as e:
            self.logger.error(f"Error while searching on collection{e}")
            return False

    def list_all_collections(self):
        return self.clint.get_collections()

    def get_collection_info(self, collection_name):
        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} is not exist")
            return False

        try:
            return self.clint.get_collection(collection_name=collection_name)

        except Exception as e:
            self.logger.error(f"Error while getting info {e}")
            return None

    def delete_collection(self, collection_name):
        if self.is_collection_exists(collection_name=collection_name):
            try:
                return self.clint.delete_collection(collection_name=collection_name)

            except Exception as e:
                self.logger.error(
                    f"Error while deleting collection {collection_name} {e}"
                )
                return False

        else:
            self.logger.error(f"Collection {collection_name} not exists to delete!")
            return False

    def create_collection(
        self,
        collection_name,
        vector_size,
        do_reset=False,
    ):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)

        if not self.is_collection_exists(collection_name=collection_name):
            try:
                self.clint.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=self.distance_method,
                    ),
                )

            except Exception as e:
                self.logger.error(
                    f"Error while creating Collection {collection_name} {e}"
                )
                return False

            self.logger.info(f"Collection {collection_name} created successfully")
            return True

    def insert_one(
        self,
        collection_name,
        vector,
        text,
        metadata=None,
        record_id=None,
    ):
        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.error(
                f"Can't insert new record to non-existed collection {collection_name}"
            )
            return False

        try:
            _ = self.clint.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata,
                        },
                    )
                ],
            )

        except Exception as e:
            self.logger.error(f"Error while inserting record {e}")
            return False

        self.logger.info("Record insertion done successfully")
        return True

    def insert_many(
        self,
        collection_name,
        vectors,
        texts,
        metadata=None,
        record_ids=None,
        batch_size=50,
    ):
        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.error(
                f"Can't insert new record to non-existed collection {collection_name}"
            )
            return False

        num_vectors = len(vectors)
        if metadata is None:
            metadata = [None] * num_vectors

        if record_ids is None:
            record_ids = [None] * num_vectors

        for i in range(0, num_vectors, batch_size):
            batch_end = i + batch_size

            batch_vectors = vectors[i:batch_end]
            batch_texts = texts[i:batch_end]
            batch_metadata = metadata[i:batch_end]

            curr_batch_size = len(batch_vectors)
            batch_records = [
                models.Record(
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x],
                    },
                )
                for x in range(curr_batch_size)
            ]

            try:
                _ = self.clint.upload_records(
                    collection_name=collection_name,
                    records=[batch_records],
                )

            except Exception as e:
                self.logger.error(f"Error while inserting batch {e}")
                return False

            self.logger.info("Insertion done successfully")
            return True

    def search_by_vector(self, collection_name, vector, limit=5):
        try:
            return self.clint.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit,
            )
        except Exception as e:
            self.logger.error(f"Error while searching a query vector {e}")
            return None
