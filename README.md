# Small package to vectorize a blob storage of videos and images [WIP]

Set values in .env
```
# Airvector
AIRVECTOR_STATE_STORAGE_CONTAINER_NAME=airvector
AIRVECTOR_FILE_STORAGE_CONTAINER_NAME=airvector-files

# OpenAI
OPENAI_API_KEY=

# Azure
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_BASE_URL=
AZURE_VISION_DEPLOYMENT_NAME=
AZURE_RESOURCE_NAME_EMBEDDINGS=
AZURE_OPENAI_API_KEY_EMBEDDINGS=

# Pinecone
PINECONE_API_KEY=
```


Install
```
poetry install
poetry shell
```

Run the example
```
import os
from airvector.pipelines.Pipeline import Pipeline

file_container = os.getenv("AIRVECTOR_FILE_STORAGE_CONTAINER_NAME")

# Run the pipeline
pipeline = Pipeline(
    storage_name="source-azure-blob-storage",
    pipeline_name="asset-to-vector-store",
    pipeline_args={
        "vision_model": "gptVision",
        "embedding_model": "text-embedding-3-large",
        "file_upload_container": file_container,
    },
    source_container="airvector-raw",
)
pipeline.run()
```