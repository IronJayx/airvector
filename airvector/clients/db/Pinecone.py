import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from loguru import logger

load_dotenv()


class PineconeClient:
    def __init__(self) -> None:
        api_key = os.environ.get("PINECONE_API_KEY")

        if not api_key:
            logger.error("PINECONE_API_KEY is not set in .env")
            return

        self.pc = Pinecone(api_key=api_key)

    def create_index(self, index_name: str, dimensions: int):
        self.pc.create_index(
            name=index_name,
            dimension=dimensions,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    def check_index_exists(self, index_name: str):
        if index_name not in self.pc.list_indexes().names():
            return False

        return True

    def connect_to_index(self, index_name: str):
        return self.pc.Index(index_name)

    def format_records(
        self, record: dict, source_id_field: str, source_embedding_field: str
    ):
        # pinecone specifics
        id = record[source_id_field]
        value = record[source_embedding_field]

        # remove for space
        del record[source_embedding_field]

        return {"id": id, "values": value, "metadata": record}

    def upsert(self, index_name: str, docs: list):
        index = self.pc.Index(index_name)
        index.upsert(docs)
