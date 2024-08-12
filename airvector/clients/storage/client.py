from loguru import logger
from airvector.utils.hasher import hash_text
from airvector.clients.storage.AzureBlobStorage import AzureBlobStorage


AvailableClients = {"source-azure-blob-storage": AzureBlobStorage}


class StorageClient:
    def __init__(self, client_name: str) -> None:
        if client_name not in AvailableClients:
            logger.error("Source is not supported yet. Add it to AvailableClients.")
            return

        self.client = AvailableClients[client_name]()

    def make_url(self, container, blob_name):
        return self.client.make_url(container=container, blob_name=blob_name)

    def read_jsonl(self, container, pattern):
        return self.client.read_jsonl(container=container, pattern=pattern)

    def read_raw(self, container, pattern):
        return self.client.read_raw(container=container, pattern=pattern)

    def download(self, container, blob_name, output_path):
        self.client.download(
            container=container, blob_name=blob_name, output_path=output_path
        )

    def upload(self, container, local_path, blob_name):
        self.client.upload(
            container=container, file_path=local_path, blob_name=blob_name
        )
