from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class KeywordConfig(BaseModel):
    required_keywords: List[str] = Field(
        ..., description="List of keywords to search for in resumes"
    )
    min_score: Optional[int] = Field(
        None, description="Minimum score threshold for filtering candidates"
    )


class ResumeAnalysis(BaseModel):
    filename: str
    text_content: str
    keywords_found: List[str]
    keywords_missing: List[str]
    score: int
    ai_summary: Optional[str] = None
    uae_presence: Optional[bool] = None
    is_image_based: bool = False
    parsed_at: datetime = Field(default_factory=datetime.now)


class FilterResponse(BaseModel):
    total_resumes: int
    valid_candidates: int
    rejected_candidates: int
    csv_file_path: str
    candidates: List[ResumeAnalysis]


class HealthResponse(BaseModel):
    status: str
    message: str


class JobProfile(BaseModel):
    """Represents a job profile with associated keywords."""

    id: str
    name: str
    description: str
    keywords: List[str]
    double_weight_keywords: List[str] = []  # Keywords that count as 2x weight
    category: str


class JobProfilesResponse(BaseModel):
    """Response containing list of job profiles."""

    profiles: List[JobProfile]
    categories: List[str]
