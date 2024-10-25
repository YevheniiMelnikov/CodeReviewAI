import hashlib
from unittest.mock import patch, AsyncMock
import pytest

from app.github_integration import GitHubClient
from app.gpt_integration import analyze_code_with_gpt, create_prompt_from_files


@pytest.mark.asyncio
async def test_get_repo_contents_paginated():
    client = GitHubClient()
    with patch(
        "httpx.AsyncClient.get",
        return_value=AsyncMock(status_code=200, json=lambda: [{"name": "file1"}]),
    ) as mock:
        result = await client.get_repo_contents_paginated(
            "https://github.com/test/test-repo"
        )
        assert result == [{"name": "file1"}]
        mock.assert_called()


@pytest.mark.asyncio
async def test_create_prompt_from_files():
    files = [
        {"name": "test_file.py", "type": "file", "download_url": "http://test-url"}
    ]
    assignment_description = "Test assignment"
    candidate_level = "junior"

    with patch("app.gpt_integration.get_file_content", return_value="File content"):
        prompt = create_prompt_from_files(
            files, assignment_description, candidate_level
        )

    assert "junior developer" in prompt
    assert "Test assignment" in prompt
    assert "test_file.py" in prompt
    assert "File content" in prompt


@pytest.mark.asyncio
async def test_analyze_code_with_gpt_cached():
    files = [
        {"name": "test_file.py", "type": "file", "download_url": "http://test-url"}
    ]
    assignment_description = "Test assignment"
    candidate_level = "junior"
    prompt_hash = hashlib.md5(
        f"{assignment_description}_{candidate_level}_{files}".encode()
    ).hexdigest()

    with patch(
        "app.gpt_integration.redis_client.get", return_value="cached result"
    ) as mock:
        result = await analyze_code_with_gpt(
            files, assignment_description, candidate_level
        )
        assert result == "cached result"
        mock.assert_called_once_with(prompt_hash)


@pytest.mark.asyncio
async def test_analyze_code_with_gpt_no_cache():
    files = [
        {"name": "test_file.py", "type": "file", "download_url": "http://test-url"}
    ]
    assignment_description = "Test assignment"
    candidate_level = "junior"
    prompt_hash = hashlib.md5(
        f"{assignment_description}_{candidate_level}_{files}".encode()
    ).hexdigest()

    with patch("app.gpt_integration.redis_client.get", return_value=None), patch(
        "app.gpt_integration.create_prompt_from_files", return_value="Test prompt"
    ), patch(
        "app.gpt_integration.ai_client.chat.completions.create",
        new=AsyncMock(
            return_value=AsyncMock(
                choices=[AsyncMock(message=AsyncMock(content="Test result"))]
            )
        ),
    ), patch(
        "app.gpt_integration.redis_client.set"
    ) as mock:
        result = await analyze_code_with_gpt(
            files, assignment_description, candidate_level
        )
        assert result == "Test result"
        mock.assert_called_once_with(prompt_hash, "Test result", ex=86400)
