import os
import json
import tempfile
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

from airvector.clients.storage.client import StorageClient


class StateManager:
    def __init__(
        self,
        storage_client: StorageClient,
        source_container: str,
    ) -> None:
        self.storage_client = storage_client
        self.source_container = source_container

        self.state_container = os.getenv("AIRVECTOR_STATE_STORAGE_CONTAINER_NAME")

        if not self.state_container:
            raise Exception(
                "AIRVECTOR_STATE_STORAGE_CONTAINER_NAME needs to be set in .env"
            )

    def set_file_pattern(self, stage: str):
        return f"source={self.source_container}/stage={stage}/*"

    def fetch_unprocessed(
        self,
        inbound_stage: str,
        outbound_stage: str,
    ):
        inbound_pattern = self.set_file_pattern(inbound_stage)
        outbound_pattern = self.set_file_pattern(outbound_stage)

        logger.info(f"Fetching for {inbound_stage} vs. {outbound_stage}")

        # special case for very first step

        if inbound_stage == "raw":
            return self.storage_client.read_raw(
                container=self.source_container, pattern=inbound_pattern
            )

        # base case

        inbound_stream = self.storage_client.read_jsonl(
            container=self.state_container, pattern=inbound_pattern
        )

        outbound_stream = self.storage_client.read_jsonl(
            container=self.state_container, pattern=outbound_pattern
        )

        # filter out already processed

        # get outbounds ids
        outbound_ids = {}
        if len(outbound_stream) > 0:
            outbound_ids = set([x["parent_airvector_id"] for x in outbound_stream])

        # return only news
        return [x for x in inbound_stream if x["airvector_id"] not in outbound_ids]

    def upload_state_file(self, entry: dict, stage: str, suffix: str = ""):
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()

        # Define the path for the temporary file
        temp_file_path = tempfile.mktemp(dir=temp_dir, suffix=".jsonl")

        # Write the dictionary to the temporary file as JSON lines
        with open(temp_file_path, "w") as temp_file:
            json.dump(entry, temp_file)

        source = entry["source"]
        id = entry["airvector_id"]
        blob_path = f"source={source}/stage={stage}/{id}{suffix}.jsonl"
        self.storage_client.upload(
            container=self.state_container,
            local_path=temp_file_path,
            blob_name=blob_path,
        )
