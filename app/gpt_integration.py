import hashlib

import httpx
import loguru
import redis
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os

load_dotenv()
ai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
redis_client = redis.from_url(
    os.getenv("REDIS_URL"), encoding="utf-8", decode_responses=True
)
logger = loguru.logger


async def analyze_code_with_gpt(files, assignment_description, candidate_level):
    prompt_hash = hashlib.md5(
        f"{assignment_description}_{candidate_level}_{files}".encode()
    ).hexdigest()
    if cached_result := redis_client.get(prompt_hash):
        return cached_result

    prompt = create_prompt_from_files(files, assignment_description, candidate_level)
    response = await ai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.5,
    )

    result = response.choices[0].message.content.strip()
    redis_client.set(prompt_hash, result, ex=86400)
    logger.info(f"Analysis result cached with hash {prompt_hash}")

    return result


def create_prompt_from_files(
    files: list[dict], assignment_description: str, candidate_level: str
) -> str:
    prompt = f"You are a code reviewer analyzing a project for a {candidate_level} developer.\n"
    prompt += f"Assignment: {assignment_description}\n\n"
    prompt += "Here are the contents of the files:\n\n"

    for file in files:
        if file["type"] == "file":
            file_content = get_file_content(file["download_url"])
            prompt += f"File: {file['name']}\n{file_content[:500]}...\n\n"

    prompt += "Please review the code for quality issues, potential improvements, and suggest a rating.\n"
    return prompt


def get_file_content(url: str) -> str:
    response = httpx.get(url)
    if response.status_code == 200:
        return response.text
    return "Failed to fetch file content"
