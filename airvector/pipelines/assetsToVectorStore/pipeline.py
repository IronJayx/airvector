from airvector.pipelines.assetsToVectorStore.steps import AssetsToVectors
from airvector.clients.storage.client import StorageClient


class AssetsToVectorPipeline:

    @staticmethod
    def set_pipeline(
        storage_client: StorageClient,
        vision_model: str = "gptVision",
        embedding_model: str = "text-embedding-3-large",
        file_upload_container: str = "airvector-files",
    ):
        pipeline_processor = AssetsToVectors(
            storage_client=storage_client, file_upload_container=file_upload_container
        )

        return {
            "raw": {
                "inbound": "raw",
                "outbound": "parsed",
                "function": lambda entry: pipeline_processor.ingest(entry),
                "upload_state": True,
            },
            "step_2": {
                "inbound": "parsed",
                "outbound": "preprocessed",
                "function": lambda entry: pipeline_processor.preprocess(entry),
                "multiple_outputs_per_entry": True,
                "upload_state": True,
            },
            "step_3": {
                "inbound": "preprocessed",
                "outbound": f"captioned/model={vision_model}",
                "function": lambda entry: pipeline_processor.vision(entry),
                "upload_state": True,
            },
            "step_4": {
                "inbound": f"captioned/model={vision_model}",
                "outbound": f"vectorized/model={embedding_model}",
                "function": lambda entry: pipeline_processor.vectorize(entry),
                "upload_state": True,
            },
            "step_5": {
                "inbound": f"vectorized/model={embedding_model}",
                "outbound": f"pinecone/always-empty",
                "function": lambda entries: pipeline_processor.index(
                    entries, index_name="test", embedding_model=embedding_model
                ),
                "batch_process": True,
                "upload_state": False,  # Not needed for index
            },
        }
