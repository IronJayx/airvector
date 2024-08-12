from loguru import logger
from airvector.clients.db.Pinecone import PineconeClient


AvailableClients = {"pinecone": PineconeClient}

AvailableEmbeddings = {"text-embedding-3-large": 3072}


class DatabaseClient:
    def __init__(self, client_name: str, embedding_model: str) -> None:
        if client_name not in AvailableClients:
            logger.error("Source is not supported yet. Add it to AvailableClients.")
            return

        if embedding_model not in AvailableEmbeddings:
            logger.error(
                "Embedding model is not supported yet. Add it to EmbeddingsDimensions."
            )
            return

        self.db = AvailableClients[client_name]()
        self.embeddings_dimensions = AvailableEmbeddings[embedding_model]

    def format_records(
        self, entries: list, source_id_field: str, source_embedding_field: str
    ):
        formatted = [
            self.db.format_records(
                record=x,
                source_id_field=source_id_field,
                source_embedding_field=source_embedding_field,
            )
            for x in entries
        ]

        return formatted

    def upsert(self, index_name: str, records: list):
        if not self.db.check_index_exists(index_name=index_name):
            self.db.create_index(
                index_name=index_name, dimensions=self.embeddings_dimensions
            )

        self.db.upsert(index_name=index_name, docs=records)
