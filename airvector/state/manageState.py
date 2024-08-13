import os
import json
import tempfile
from loguru import logger

from airvector.clients.storage.client import StorageClient


RAW_CONTAINER = os.environ.get("AZURE_RAW_STORAGE_CONTAINER_NAME")
STATE_CONTAINER = os.environ.get("AZURE_STATE_STORAGE_CONTAINER_NAME")


def set_file_pattern(source: str, stage: str):
    return f"source={source}/stage={stage}/*"


def fetch_unprocessed(
    storage_client: StorageClient,
    inbound_stage: str,
    outbound_stage: str,
    source: str = "*",
):
    inbound_pattern = set_file_pattern(source, inbound_stage)
    outbound_pattern = set_file_pattern(source, outbound_stage)

    logger.info(f"Fetching for {inbound_stage} vs. {outbound_stage}")

    # special case for very first step

    if inbound_stage == "raw":
        return storage_client.read_raw(container=RAW_CONTAINER, pattern=inbound_pattern)

    # base case

    inbound_stream = storage_client.read_jsonl(
        container=STATE_CONTAINER, pattern=inbound_pattern
    )

    outbound_stream = storage_client.read_jsonl(
        container=STATE_CONTAINER, pattern=outbound_pattern
    )

    # filter out already processed

    # get outbounds ids
    outbound_ids = {}
    if len(outbound_stream) > 0:
        outbound_ids = set([x["parent_airvector_id"] for x in outbound_stream])

    # return only news
    return [x for x in inbound_stream if x["airvector_id"] not in outbound_ids]


def upload_state_file(
    storage_client: StorageClient, entry: dict, stage: str, suffix: str = ""
):
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
    storage_client.upload(
        container=STATE_CONTAINER, local_path=temp_file_path, blob_name=blob_path
    )
