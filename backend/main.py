from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List
import json
from datetime import datetime

from models import (
    ResumeAnalysis,
    FilterResponse,
    HealthResponse
)
from resume_parser import ResumeParser
from keyword_matcher import KeywordMatcher
from openai_service import OpenAIService
from csv_exporter import CSVExporter
from config import settings

app = FastAPI(
    title="Resume Filter API",
    description="API for parsing, analyzing, and filtering resumes based on keywords with AI summaries",
    version="1.0.0"
)


@app.get("/", response_model=HealthResponse)
async def root():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        message="Resume Filter API is running"
    )


@app.post("/filter-resumes", response_model=FilterResponse)
async def filter_resumes(
    files: List[UploadFile] = File(..., description="Resume files (PDF or DOCX)"),
    keywords: str = Form(..., description="JSON array of keywords to search for"),
    min_score: int = Form(None, description="Minimum score threshold (0-100)"),
    generate_ai_summary: bool = Form(True, description="Generate AI summaries using OpenAI")
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
            detail=f"Invalid keywords format. Expected JSON array: {str(e)}"
        )

    # Use provided min_score or fall back to config
    threshold = min_score if min_score is not None else settings.min_keyword_score

    # Process each resume
    all_analyses = []

    for file in files:
        try:
            # Read file content
            content = await file.read()

            # Parse resume
            text = ResumeParser.parse_resume(file.filename, content)

            # Analyze keywords
            found, missing, score = KeywordMatcher.analyze_resume(
                text,
                keyword_list
            )

            # Create analysis object
            analysis = ResumeAnalysis(
                filename=file.filename,
                text_content=text,
                keywords_found=found,
                keywords_missing=missing,
                score=score,
                parsed_at=datetime.now()
            )

            all_analyses.append(analysis)

        except Exception as e:
            # Log error but continue processing other files
            print(f"Error processing {file.filename}: {str(e)}")
            continue

    # Filter valid candidates
    valid_candidates = [
        analysis for analysis in all_analyses
        if analysis.score >= threshold
    ]

    # Generate AI summaries for valid candidates if requested
    if generate_ai_summary and valid_candidates and settings.use_openai:
        try:
            openai_service = OpenAIService()
            for candidate in valid_candidates:
                candidate.ai_summary = openai_service.generate_resume_summary(
                    candidate.text_content,
                    candidate.keywords_found,
                    candidate.keywords_missing,
                    candidate.score
                )
        except Exception as e:
            print(f"Error generating AI summaries: {str(e)}")
            # Continue without AI summaries
    elif generate_ai_summary and not settings.use_openai:
        print("OpenAI feature is disabled. Skipping AI summary generation.")

    # Export to CSV
    if valid_candidates:
        csv_path = CSVExporter.create_timestamped_path(settings.csv_output_path)
        CSVExporter.export_to_csv(
            valid_candidates, 
            csv_path,
            resume_folder_path=settings.resume_folder_path
        )
    else:
        csv_path = "No valid candidates found - CSV not generated"

    return FilterResponse(
        total_resumes=len(all_analyses),
        valid_candidates=len(valid_candidates),
        rejected_candidates=len(all_analyses) - len(valid_candidates),
        csv_file_path=csv_path,
        candidates=valid_candidates
    )


@app.get("/download-csv")
async def download_csv(file_path: str):
    """
    Download a generated CSV file

    Args:
        file_path: Path to the CSV file to download

    Returns:
        FileResponse with the CSV file
    """
    import os

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="CSV file not found"
        )

    return FileResponse(
        path=file_path,
        media_type='text/csv',
        filename=os.path.basename(file_path)
    )


@app.post("/analyze-single", response_model=ResumeAnalysis)
async def analyze_single_resume(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    keywords: str = Form(..., description="JSON array of keywords to search for"),
    generate_ai_summary: bool = Form(True, description="Generate AI summary using OpenAI")
):
    """
    Analyze a single resume without filtering or CSV export

    Args:
        file: Resume file (PDF or DOCX format)
        keywords: JSON string array of keywords to search for
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
            detail=f"Invalid keywords format. Expected JSON array: {str(e)}"
        )

    try:
        # Read and parse resume
        content = await file.read()
        text = ResumeParser.parse_resume(file.filename, content)

        # Analyze keywords
        found, missing, score = KeywordMatcher.analyze_resume(text, keyword_list)

        # Create analysis object
        analysis = ResumeAnalysis(
            filename=file.filename,
            text_content=text,
            keywords_found=found,
            keywords_missing=missing,
            score=score,
            parsed_at=datetime.now()
        )

        # Generate AI summary if requested
        if generate_ai_summary and settings.use_openai:
            openai_service = OpenAIService()
            analysis.ai_summary = openai_service.generate_resume_summary(
                text,
                found,
                missing,
                score
            )
        elif generate_ai_summary and not settings.use_openai:
            analysis.ai_summary = "OpenAI feature is disabled"

        return analysis

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing resume: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



