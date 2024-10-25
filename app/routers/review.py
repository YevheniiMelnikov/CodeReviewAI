import loguru
from fastapi import APIRouter, HTTPException

from ..github_integration import GitHubClient
from ..gpt_integration import analyze_code_with_gpt
from ..models.review import ReviewRequest, ReviewResponse


router = APIRouter()
logger = loguru.logger


@router.post("/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest) -> ReviewResponse:
    logger.info(f"Received review request for repository: {request.github_url}")
    github_client = GitHubClient()
    try:
        files = await github_client.get_repo_contents_paginated(request.github_url)
        logger.info("Successfully fetched repository contents")
        analysis = await analyze_code_with_gpt(
            files, request.assignment_description, request.candidate_level
        )
    except HTTPException as e:
        logger.error(f"Error during processing: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    logger.info(f"Analysis completed successfully for repository: {request.github_url}")
    return ReviewResponse(analysis=analysis)
