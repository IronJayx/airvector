# Small package to vectorize a blob storage of videos and images [WIP]

Set values in .env
```
# OpenAI
OPENAI_API_KEY=""

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=""
AZURE_STORAGE_BASE_URL =""
AZURE_STORAGE_ACCOUNT_KEY=""
AZURE_STORAGE_ACCOUNT_NAME=""

# Airvector
AZURE_STATE_STORAGE_CONTAINER_NAME=""
AZURE_FILE_STORAGE_CONTAINER_NAME=""
AZURE_RAW_STORAGE_CONTAINER_NAME=""

# Azure OpenAI
AZURE_RESOURCE_NAME_EMBEDDINGS=""
AZURE_API_VERSION=""
AZURE_OPENAI_API_KEY_EMBEDDINGS=""
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_ID=""

PINECONE_API_KEY=""
```


Run example
```
poetry install
poetry shell

python airvector/pipelines/assetsToVectorStore/runner.py
```