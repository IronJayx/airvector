import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError


class AzureBlobStorage:

    def __init__(self) -> None:
        super().__init__()

        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        storage_base_url = os.environ.get("AZURE_STORAGE_BASE_URL")

        if not connection_string:
            raise Exception(
                f"AzureBlobStorage: connection string missing from .env, got {connection_string}"
            )

        self.client = BlobServiceClient.from_connection_string(connection_string)
        self.storage_base_url = storage_base_url

    def download(self, container: str, blob_name: str, output_path: str):
        container_client = self.set_container(container=container)

        with open(file=output_path, mode="wb") as download_file:
            download_file.write(container_client.download_blob(blob_name).readall())

        return output_path

    def upload(self, container: str, file_path: str, blob_name: str):
        """Returns a dict (hash(url): blob_data)"""

        print(f"Uploading {container} {blob_name}")

        # logger.info(f'Writing blob to {self.container_name} under {blob_name}')
        blob_client = self.client.get_blob_client(container=container, blob=blob_name)

        with open(file=file_path, mode="rb") as data:
            try:
                blob_client.upload_blob(data=data, overwrite=True)
            except:
                logger.info(
                    f"Container did not exist, creating new container: {container}"
                )
                self.client.create_container(name=container, public_access="blob")

                logger.info(f"Container {container} was created")
                self.upload(
                    container=container, file_path=file_path, blob_name=blob_name
                )

    def make_url(self, container: str, blob_name: str):
        from urllib.parse import urljoin

        return urljoin(self.storage_base_url, f"{container}/{blob_name}")

    def read_raw(self, container: str, pattern: str) -> list:
        import fnmatch

        container_client = self.set_container(container)
        blobs = container_client.list_blobs()

        results = []
        for blob in blobs:
            blob_name = blob.name

            if fnmatch.fnmatch(blob_name, pattern):
                results.append(
                    {
                        "container": container,
                        "path": blob_name,
                        "url": self.make_url(container=container, blob_name=blob_name),
                    }
                )

        return results

    def read_jsonl(self, container: str, pattern: str) -> list:
        import fnmatch
        import json

        container_client = self.set_container(container)
        blobs = container_client.list_blobs()

        results = []
        for blob in blobs:
            blob_name = blob.name

            if fnmatch.fnmatch(blob_name, pattern):
                output_path = f"/tmp/{blob_name.replace('/', '_')}"  # Ensure the path is unique and valid
                self.download(container, blob_name, output_path)

                with open(output_path, "r") as f:
                    for line in f:
                        results.append(json.loads(line))

        return results

    def set_container(self, container: str):
        try:
            return self.client.get_container_client(container=container)
        except ResourceNotFoundError:
            logger.debug(f"Container with name: {container} was not found.")
            self.client.list_containers()
        except Exception as e:
            logger.error(f"Error fetching container: {container} {e}.")
