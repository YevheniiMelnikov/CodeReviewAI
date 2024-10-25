from fastapi import FastAPI
from .routers import review


app = FastAPI(
    title="CodeAnalyzer",
    description="Service to analyze code with OpenAI and GitHub API",
    version="1.0.0",
)

app.include_router(review.router)
