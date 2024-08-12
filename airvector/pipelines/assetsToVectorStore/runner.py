import os
from loguru import logger

from airvector.pipelines.assetsToVectorStore.stepsCode import AssetsToVectors
from airvector.clients.storage.client import StorageClient
from airvector.state.manageState import fetch_unprocessed, upload_state_file

# global params
SOURCE_NAME = "source-azure-blob-storage"
EMBEDDING_MODEL = "text-embedding-3-large"

# Initialize
storage_client = StorageClient(client_name=SOURCE_NAME)
pipeline = AssetsToVectors(storage_client=storage_client)

# Define pipeline steps
pipeline_steps = {
    "step_1": {
        "inbound": "raw",
        "outbound": "parsed",
        "function": lambda entry: pipeline.ingest(entry),
        "upload_stage": "parsed",
        "upload_state": True,
    },
    "step_2": {
        "inbound": "parsed",
        "outbound": "preprocessed",
        "function": lambda entry: pipeline.preprocess(entry),
        "upload_stage": "preprocessed",
        "multiple_outputs_per_entry": True,
        "upload_state": True,
    },
    "step_3": {
        "inbound": "preprocessed",
        "outbound": "captioned/model=gptVision",
        "function": lambda entry: pipeline.vision(entry),
        "upload_stage": "captioned/model=gptVision",
        "upload_state": True,
    },
    "step_4": {
        "inbound": "captioned/model=gptVision",
        "outbound": f"vectorized/model={EMBEDDING_MODEL}",
        "function": lambda entry: pipeline.vectorize(entry),
        "upload_stage": f"vectorized/model={EMBEDDING_MODEL}",
        "upload_state": True,
    },
    "step_5": {
        "inbound": f"vectorized/model={EMBEDDING_MODEL}",
        "outbound": f"pinecone/always-empty",
        "function": lambda entries: pipeline.index(
            entries, index_name="test", embedding_model=EMBEDDING_MODEL
        ),
        "batch_process": True,
        "upload_state": False,  # Not needed for index
    },
}


def update_state(step: dict, result: list):
    if not step.get("upload_state"):
        return

    if step.get("multiple_outputs_per_entry"):
        for idx, sub_entry in enumerate(result):
            upload_state_file(
                storage_client=storage_client,
                entry=sub_entry,
                stage=step["upload_stage"],
                suffix=idx,
            )
    else:
        upload_state_file(
            storage_client=storage_client,
            entry=result,
            stage=step["upload_stage"],
        )


def run_pipeline_step(step_name):
    step = pipeline_steps[step_name]
    unprocessed_data = fetch_unprocessed(
        storage_client=storage_client,
        inbound=step["inbound"],
        outbound=step.get("outbound"),
    )

    if not unprocessed_data:
        print(f"All processed for {step_name}")
        return

    if step.get("batch_process"):
        # If batch_process is True, process all data at once
        result = step["function"](unprocessed_data)
        update_state(step=step, result=result)
    else:
        # Process each entry individually
        for entry in unprocessed_data:
            result = step["function"](entry)
            update_state(step=step, result=result)


# Run pipeline
for step_name in pipeline_steps.keys():
    run_pipeline_step(step_name)
