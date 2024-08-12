import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


def get_embedding(text: str) -> list[float]:
    api_key = os.getenv("AZURE_OPENAI_API_KEY_EMBEDDINGS")

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY_EMBEDDINGS"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_RESOURCE_NAME_EMBEDDINGS"),
    )

    response = client.embeddings.create(input=text, model="text-embedding-3-large")

    return response.data[0].embedding
