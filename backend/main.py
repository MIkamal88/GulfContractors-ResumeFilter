from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from typing import List, Dict
import json
from datetime import datetime

from models import (
    EmploymentEntry,
    ResumeAnalysis,
    FilterResponse,
    HealthResponse,
    JobProfile,
    JobProfilesResponse,
)
from job_profiles_manager import JobProfilesManager
from resume_parser import ResumeParser
from keyword_matcher import KeywordMatcher
from openai_service import OpenAIService
from csv_exporter import CSVExporter
from config import settings

app = FastAPI(
    title="Resume Filter API",
    description="API for parsing, analyzing, and filtering resumes based on keywords with AI summaries",
    version="1.0.0",
)

# Configure CORS - parse origins from settings (comma-separated or *)
cors_origins = (
    ["*"]
    if settings.cors_origins == "*"
    else [origin.strip() for origin in settings.cors_origins.split(",")]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# In-memory storage for uploaded resumes (filename -> file content)
resume_storage: Dict[str, bytes] = {}

# Initialize job profiles manager with file persistence
profiles_manager = JobProfilesManager(storage_file=settings.storage_json)


@api_router.get("/", response_model=HealthResponse)
async def root():
    """
    Health check endpoint
    """
    return HealthResponse(status="healthy", message="Resume Filter API is running")


@api_router.post("/filter-resumes", response_model=FilterResponse)
async def filter_resumes(
    files: List[UploadFile] = File(..., description="Resume files (PDF or DOCX)"),
    keywords: str = Form(..., description="JSON array of keywords to search for"),
    double_weight_keywords: str = Form(
        "[]", description="JSON array of keywords that count as 2x weight"
    ),
    min_score: int = Form(None, description="Minimum score threshold (0-100)"),
    generate_ai_summary: bool = Form(
        True, description="Generate AI summaries using OpenAI"
    ),
):
    """
    Upload multiple resumes, filter by keywords, and export valid candidates to CSV

    Args:
        files: List of resume files (PDF or DOCX format)
        keywords: JSON string array of keywords to search for
        min_score: Minimum score threshold for filtering (optional, uses config default if not provided)
        generate_ai_summary: Whether to generate AI summaries (default: True)

    Returns:
        FilterResponse with analysis results and CSV file path
    """
    # Parse keywords
    try:
        keyword_list = json.loads(keywords)
        if not isinstance(keyword_list, list) or len(keyword_list) == 0:
            raise ValueError("Keywords must be a non-empty array")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid keywords format. Expected JSON array: {str(e)}",
        )

    # Parse double-weight keywords
    try:
        double_weight_list = json.loads(double_weight_keywords)
        if not isinstance(double_weight_list, list):
            raise ValueError("Double-weight keywords must be an array")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid double_weight_keywords format. Expected JSON array: {str(e)}",
        )

    # Use provided min_score or fall back to config
    threshold = min_score if min_score is not None else settings.min_keyword_score

    # Process each resume
    all_analyses = []

    for file in files:
        try:
            # Read file content
            content = await file.read()

            # Store file content in memory for later retrieval
            resume_storage[file.filename] = content

            # Parse resume (returns text and is_image_based flag)
            text, is_image_based = ResumeParser.parse_resume(file.filename, content)

            # Analyze keywords with double-weight support
            found, missing, score = KeywordMatcher.analyze_resume(
                text, keyword_list, double_weight_list
            )

            # Create analysis object
            analysis = ResumeAnalysis(
                filename=file.filename,
                text_content=text,
                keywords_found=found,
                keywords_missing=missing,
                score=score,
                is_image_based=is_image_based,
                parsed_at=datetime.now(),
            )

            all_analyses.append(analysis)

        except Exception as e:
            # Log error but continue processing other files
            print(f"Error processing {file.filename}: {str(e)}")
            continue

    # Filter valid candidates
    valid_candidates = [
        analysis for analysis in all_analyses if analysis.score >= threshold
    ]

    # Sort valid candidates by score in descending order
    valid_candidates.sort(key=lambda x: x.score, reverse=True)

    # Generate AI summaries and detect UAE presence for valid candidates if requested
    # Skip image-based resumes to save API usage
    if generate_ai_summary and valid_candidates and settings.use_openai:
        try:
            openai_service = OpenAIService()
            for candidate in valid_candidates:
                if candidate.is_image_based:
                    # Skip AI processing for image-based resumes
                    continue
                result = openai_service.generate_resume_summary(
                    candidate.text_content,
                    candidate.keywords_found,
                    candidate.keywords_missing,
                    candidate.score,
                )
                candidate.ai_summary = result.get("summary")
                candidate.uae_presence = result.get("uae_presence")
                # Map employment history
                raw_history = result.get("employment_history")
                if raw_history and isinstance(raw_history, list):
                    candidate.employment_history = [
                        EmploymentEntry(**entry)
                        for entry in raw_history
                        if isinstance(entry, dict)
                    ]
                candidate.total_experience_years = result.get("total_experience_years")
        except Exception as e:
            print(f"Error generating AI summaries: {str(e)}")
            # Continue without AI summaries
    elif generate_ai_summary and not settings.use_openai:
        print("OpenAI feature is disabled. Skipping AI summary generation.")

    # Generate timestamp for CSV identification
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"filtered_resumes_{timestamp}.csv"

    return FilterResponse(
        total_resumes=len(all_analyses),
        valid_candidates=len(valid_candidates),
        rejected_candidates=len(all_analyses) - len(valid_candidates),
        csv_file_path=csv_filename
        if valid_candidates
        else "No valid candidates found - CSV not generated",
        candidates=valid_candidates,
    )


@api_router.post("/download-csv")
async def download_csv(candidates: List[ResumeAnalysis]):
    """
    Generate and download CSV from candidate data

    Args:
        candidates: List of ResumeAnalysis objects to export

    Returns:
        StreamingResponse with the CSV file
    """
    if not candidates:
        raise HTTPException(
            status_code=400, detail="No candidates provided for CSV generation"
        )

    # Generate CSV content in memory
    csv_buffer = CSVExporter.export_to_csv_buffer(candidates)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"filtered_resumes_{timestamp}.csv"

    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@api_router.get("/view-resume/{filename}")
async def view_resume(filename: str):
    """
    Serve a resume file for viewing from in-memory storage

    Args:
        filename: Name of the resume file to view

    Returns:
        Response with the file content
    """
    import os

    # Get file from in-memory storage
    if filename not in resume_storage:
        raise HTTPException(
            status_code=404,
            detail="Resume file not found. File may have been cleared from memory.",
        )

    file_content = resume_storage[filename]

    # Determine the media type based on file extension
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension == ".pdf":
        media_type = "application/pdf"
    elif file_extension in [".doc", ".docx"]:
        media_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        media_type = "application/octet-stream"

    return Response(
        content=file_content,
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@api_router.post("/analyze-single", response_model=ResumeAnalysis)
async def analyze_single_resume(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    keywords: str = Form(..., description="JSON array of keywords to search for"),
    double_weight_keywords: str = Form(
        "[]", description="JSON array of keywords that count as 2x weight"
    ),
    generate_ai_summary: bool = Form(
        True, description="Generate AI summary using OpenAI"
    ),
):
    """
    Analyze a single resume without filtering or CSV export

    Args:
        file: Resume file (PDF or DOCX format)
        keywords: JSON string array of keywords to search for
        double_weight_keywords: JSON array of keywords that count as 2x weight
        generate_ai_summary: Whether to generate AI summary (default: True)

    Returns:
        ResumeAnalysis object with analysis results
    """
    # Parse keywords
    try:
        keyword_list = json.loads(keywords)
        if not isinstance(keyword_list, list) or len(keyword_list) == 0:
            raise ValueError("Keywords must be a non-empty array")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid keywords format. Expected JSON array: {str(e)}",
        )

    # Parse double-weight keywords
    try:
        double_weight_list = json.loads(double_weight_keywords)
        if not isinstance(double_weight_list, list):
            raise ValueError("Double-weight keywords must be an array")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid double_weight_keywords format. Expected JSON array: {str(e)}",
        )

    try:
        # Read and parse resume (returns text and is_image_based flag)
        content = await file.read()
        text, is_image_based = ResumeParser.parse_resume(file.filename, content)

        # Analyze keywords with double-weight support
        found, missing, score = KeywordMatcher.analyze_resume(
            text, keyword_list, double_weight_list
        )

        # Create analysis object
        analysis = ResumeAnalysis(
            filename=file.filename,
            text_content=text,
            keywords_found=found,
            keywords_missing=missing,
            score=score,
            is_image_based=is_image_based,
            parsed_at=datetime.now(),
        )

        # Generate AI summary, detect UAE presence, and extract employment history
        # Skip for image-based resumes to save API usage
        if generate_ai_summary and settings.use_openai and not is_image_based:
            openai_service = OpenAIService()
            result = openai_service.generate_resume_summary(text, found, missing, score)
            analysis.ai_summary = result.get("summary")
            analysis.uae_presence = result.get("uae_presence")
            # Map employment history
            raw_history = result.get("employment_history")
            if raw_history and isinstance(raw_history, list):
                analysis.employment_history = [
                    EmploymentEntry(**entry)
                    for entry in raw_history
                    if isinstance(entry, dict)
                ]
            analysis.total_experience_years = result.get("total_experience_years")
        elif generate_ai_summary and not settings.use_openai:
            analysis.ai_summary = "OpenAI feature is disabled"

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")


@api_router.get("/job-profiles", response_model=JobProfilesResponse)
async def get_job_profiles():
    """
    Get all available job profiles (default + custom)

    Returns:
        JobProfilesResponse with list of profiles and categories
    """
    all_profiles = profiles_manager.get_all_profiles()
    categories = profiles_manager.get_categories()

    return JobProfilesResponse(profiles=all_profiles, categories=categories)


@api_router.get("/job-profiles/{profile_id}", response_model=JobProfile)
async def get_job_profile(profile_id: str):
    """
    Get a specific job profile by ID

    Args:
        profile_id: The ID of the job profile

    Returns:
        JobProfile object
    """
    profile = profiles_manager.get_profile_by_id(profile_id)

    if profile is None:
        raise HTTPException(
            status_code=404, detail=f"Job profile '{profile_id}' not found"
        )

    return profile


@api_router.post("/job-profiles", response_model=JobProfile)
async def create_custom_profile(profile: JobProfile):
    """
    Create a custom job profile (persisted to file)

    Args:
        profile: JobProfile object to create

    Returns:
        The created JobProfile
    """
    try:
        return profiles_manager.add_custom_profile(profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating profile: {str(e)}")


@api_router.put("/job-profiles/{profile_id}", response_model=JobProfile)
async def update_custom_profile(profile_id: str, profile: JobProfile):
    """
    Update a custom job profile (only custom profiles can be updated)

    Args:
        profile_id: The ID of the profile to update
        profile: Updated JobProfile object

    Returns:
        The updated JobProfile
    """
    try:
        updated_profile = profiles_manager.update_custom_profile(profile_id, profile)

        if updated_profile is None:
            raise HTTPException(
                status_code=404, detail=f"Custom profile '{profile_id}' not found"
            )

        return updated_profile
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


@api_router.delete("/job-profiles/{profile_id}")
async def delete_custom_profile(profile_id: str):
    """
    Delete a custom job profile (only custom profiles can be deleted)

    Args:
        profile_id: The ID of the profile to delete

    Returns:
        Success message
    """
    try:
        success = profiles_manager.delete_custom_profile(profile_id)

        if not success:
            raise HTTPException(
                status_code=404, detail=f"Custom profile '{profile_id}' not found"
            )

        return {"message": f"Profile '{profile_id}' deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting profile: {str(e)}")


# Include the API router in the app
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
