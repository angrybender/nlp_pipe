import logging

logger = logging.getLogger()


from qdrant_client import QdrantClient
from qdrant_client.http import models


class DatasetIndexer:
    def __init__(self, hostname, port, collection_name):
        self.client = QdrantClient(hostname, port=int(port))
        self.collection_name = collection_name

    def index_data(self, payload, vectors, from_id_generate=0):
        ids = [from_id_generate + _id for _id in range(len(payload))]

        self.client.upsert(
            collection_name=self.collection_name,
            points=models.Batch(
                ids=ids,
                payloads=payload,
                vectors=vectors,
            ),
        )