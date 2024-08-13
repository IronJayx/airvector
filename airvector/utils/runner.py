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
