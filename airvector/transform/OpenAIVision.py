import os
from openai import OpenAI
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

from airvector.utils.prompts import Prompts


def describeImage(image_url: str, image_string: str):
    openai_key = os.environ.get("OPENAI_API_KEY")

    if not openai_key:
        logger.error("OPENAI_API_KEY needs to be set in .env")

    client = OpenAI(api_key=openai_key)

    results = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": Prompts["vision-description"]["system_prompt"],
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Image name: {image_string}",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                ],
            },
        ],
        max_tokens=500,
        temperature=0.0,
    )

    return results.choices[0].message.content
