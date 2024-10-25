from typing import Any

import httpx
import os

import loguru
from fastapi import HTTPException
from pydantic import HttpUrl

GITHUB_API_URL = "https://api.github.com"
logger = loguru.logger


class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise HTTPException(status_code=500, detail="GitHub token not found")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def get_repo_contents(self, repo_url: HttpUrl) -> dict[str, Any]:
        owner, repo_name = self.extract_repo_info(repo_url)
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo_name}/contents"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self.headers)

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Repository not found")
            elif response.status_code == 403:
                raise HTTPException(
                    status_code=403,
                    detail="Rate limit exceeded or insufficient permissions",
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch repository contents",
                )

            return response.json()

    async def get_repo_contents_paginated(
        self, repo_url: HttpUrl
    ) -> list[dict[str, Any]]:
        logger.info(f"Fetching contents of repository: {repo_url}")
        owner, repo_name = self.extract_repo_info(repo_url)
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo_name}/contents"
        page = 1
        all_contents = []
        last_fetched = None

        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                logger.info(f"Fetching page {page}")
                response = await client.get(
                    url, headers=self.headers, params={"page": page}
                )
                logger.info(f"Response status: {response.status_code}")

                if response.status_code != 200:
                    logger.error(f"Failed to fetch repository contents at page {page}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to fetch repository contents",
                    )

                contents = response.json()
                logger.info(f"Fetched {len(contents)} items from page {page}")

                if contents == last_fetched:
                    logger.info(
                        "No new content, exiting loop to prevent infinite pagination"
                    )
                    break

                last_fetched = contents

                if not contents:
                    logger.info("No more contents to fetch, exiting loop")
                    break

                all_contents.extend(contents)
                page += 1

        logger.info(f"Total items fetched: {len(all_contents)}")
        return all_contents

    @staticmethod
    def extract_repo_info(repo_url: HttpUrl) -> tuple[str, str]:
        parts = str(repo_url).rstrip("/").split("/")
        owner = parts[-2]
        repo_name = parts[-1]
        return owner, repo_name
