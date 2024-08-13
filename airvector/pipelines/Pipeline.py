from loguru import logger

from airvector.state.manageState import StateManager
from airvector.pipelines.assetsToVectorStore.pipeline import AssetsToVectorPipeline
from airvector.clients.storage.client import StorageClient

AvailablePipelines = {"asset-to-vector-store": AssetsToVectorPipeline}


class Pipeline:

    def __init__(
        self,
        storage_name: str,
        pipeline_name: str,
        pipeline_args: dict,
        source_container: str,
    ):
        self.storage_client = StorageClient(storage_name)
        self.state = StateManager(
            storage_client=self.storage_client,
            source_container=source_container,
        )
        self.source = source_container

        self.steps = self.set_pipeline(pipeline_name, pipeline_args)

    def set_pipeline(self, pipeline_name: str, pipeline_args: dict):
        if pipeline_name not in AvailablePipelines:
            raise (f"{pipeline_name} not implemented.")

        pipeline = AvailablePipelines.get(pipeline_name)

        return pipeline.set_pipeline(
            storage_client=self.storage_client,
            vision_model=pipeline_args.get("vision_model"),
            embedding_model=pipeline_args.get("embedding_model"),
            file_upload_container=pipeline_args.get("file_upload_container"),
        )

    def update_state(self, step: dict, result: list):
        if not step.get("upload_state"):
            return

        if step.get("multiple_outputs_per_entry"):
            for idx, sub_entry in enumerate(result):
                self.state.upload_state_file(
                    entry=sub_entry,
                    stage=step["upload_stage"],
                    suffix=idx,
                )
        else:
            self.state.upload_state_file(
                entry=result,
                stage=step["upload_stage"],
            )

    def run_step(self, step_name):
        step = self.steps[step_name]
        unprocessed_data = self.state.fetch_unprocessed(
            inbound_stage=step.get("inbound"),
            outbound_stage=step.get("outbound"),
        )

        if not unprocessed_data:
            logger.info(f"All processed for {step_name}")
            return

        if step.get("batch_process"):
            # If batch_process is True, process all data at once
            result = step["function"](unprocessed_data)
            self.update_state(step=step, result=result)
        else:
            # Process each entry individually
            for entry in unprocessed_data:
                result = step["function"](entry)
                self.update_state(step=step, result=result)

    def run(self):
        for step_name in self.steps.keys():
            self.run_step(step_name)
