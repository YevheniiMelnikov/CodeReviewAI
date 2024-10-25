from pydantic import BaseModel, HttpUrl
from enum import Enum


class CandidateLevel(str, Enum):
    junior = "junior"
    middle = "middle"
    senior = "senior"


class ReviewRequest(BaseModel):
    assignment_description: str
    github_url: HttpUrl
    candidate_level: CandidateLevel


class ReviewResponse(BaseModel):
    analysis: str
