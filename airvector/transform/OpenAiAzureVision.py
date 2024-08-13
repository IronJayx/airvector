import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

from airvector.utils.prompts import Prompts


def describeImage(image_url: str) -> list[float]:
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY_EMBEDDINGS"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_RESOURCE_NAME_EMBEDDINGS"),
    )

    response = client.chat.completions.create(
        model=os.getenv("AZURE_VISION_DEPLOYMENT_NAME"),
        messages=[
            {
                "role": "system",
                "content": Prompts["vision-description"]["system_prompt"],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this picture:"},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ],
        max_tokens=500,
    )

    return response.choices[0].message.content
