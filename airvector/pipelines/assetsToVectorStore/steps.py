import os
import tempfile
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

from airvector.transform.VideoToImages import video_to_images
from airvector.transform.OpenAiAzureVision import describeImage
from airvector.transform.OpenAiAzureEmbedding import get_embedding
from airvector.transform.ComputeImageLayout import compute_layout
from airvector.utils.hasher import hash_text
from airvector.clients.storage.client import StorageClient
from airvector.clients.db.client import DatabaseClient

VideoFormats = {"mp4", "avi", "mov"}


class AssetsToVectors:

    def __init__(
        self, storage_client: StorageClient, file_upload_container: str
    ) -> None:
        self.storage_client = storage_client
        self.file_upload_container = file_upload_container

        if not self.file_upload_container:
            logger.error(
                "AIRVECTOR_FILE_STORAGE_CONTAINER_NAME needs to be set in .env to store files"
            )

    def make_id(self, field: str):
        return hash_text(field)

    def ingest(self, entry: dict, id_field: str = "url"):
        file_id = self.make_id(entry[id_field])
        return {**entry, "source": entry["container"], "airvector_id": file_id}

    def preprocess(self, entry: dict):
        """
        Takes jsonl, download file locally, process according to type (upload video frames), returns jsonl.
        """
        container = entry["container"]
        path = entry["path"]
        filetype = path.split(".")[-1]
        filename = path.split("/")[-1]
        is_image = True if filetype not in VideoFormats else False

        # temp
        temp_dir = tempfile.mkdtemp()
        local_path = os.path.join(temp_dir, filename)

        # download
        self.storage_client.download(
            container=container,
            blob_name=path,
            output_path=local_path,
        )

        if is_image:
            if "image_url" not in entry:
                entry["image_url"] = entry["url"]
            if "parent_airvector_id" not in entry:
                entry["parent_airvector_id"] = entry["airvector_id"]
            entry["layout"] = compute_layout(local_path)
            return [entry]

        frames = video_to_images(local_path)

        entry["container"] = self.file_upload_container
        entry["inbound_filetype"] = "video"
        entry["inbound_container"] = container
        entry["inbound_filepath"] = path
        inbound_id = entry["airvector_id"]

        frame_entries = []
        for frame_position, frame_path in frames:
            frame_entry = entry.copy()
            frame_entry["path"] = os.path.join(inbound_id, frame_path.split("/")[-1])

            # id switch
            frame_entry["airvector_id"] = f"{inbound_id}-{frame_position}"
            frame_entry["parent_airvector_id"] = inbound_id

            self.storage_client.upload(
                container=self.file_upload_container,
                local_path=frame_path,
                blob_name=frame_entry["path"],
            )

            frame_entry["image_url"] = self.storage_client.make_url(
                container=frame_entry["container"], blob_name=frame_entry["path"]
            )

            frame_entries.extend(self.preprocess(frame_entry))

        return frame_entries

    def vision(self, entry: dict):
        description = describeImage(image_url=entry["image_url"])
        return {
            **entry,
            "vision_description": description,
            "parent_airvector_id": entry["airvector_id"],
        }

    def vectorize(self, entry: dict):
        embedding = get_embedding(text=entry["vision_description"])
        return {
            **entry,
            "embedding": embedding,
            "parent_airvector_id": entry["airvector_id"],
        }

    def index(self, entries: list, index_name: str, embedding_model: str):
        pinecone = DatabaseClient(
            client_name="pinecone", embedding_model=embedding_model
        )

        records = pinecone.format_records(
            entries=entries,
            source_id_field="airvector_id",
            source_embedding_field="embedding",
        )

        return pinecone.upsert(
            index_name=f"{index_name}-{embedding_model}", records=records
        )
