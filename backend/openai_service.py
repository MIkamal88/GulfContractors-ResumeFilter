from openai import OpenAI
from typing import Optional
from config import settings


class OpenAIService:
    """
    Service for generating AI summaries of resumes using OpenAI API
    """

    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError(
                "OpenAI API key is not configured. Please set OPENAI_API_KEY in your .env file."
            )
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_resume_summary(
        self, resume_text: str, keywords_found: list, keywords_missing: list, score: int
    ) -> str:
        """
        Generate an AI summary of the resume

        Args:
            resume_text: Full text content of the resume
            years_of_xp: Years of actual experience
            keywords_found: List of keywords found in the resume
            keywords_missing: List of keywords missing from the resume
            score: Calculated keyword match score

        Returns:
            AI-generated summary of the resume
        """
        try:
            prompt = f"""
You are an expert recruiter analyzing a candidate's resume.

Resume Content:
{resume_text[:3000]}  # Limit to first 3000 chars to manage token usage

Keyword Analysis:
- Match Score: {score}%
- Keywords Found: {", ".join(keywords_found) if keywords_found else "None"}
- Keywords Missing: {", ".join(keywords_missing) if keywords_missing else "None"}

Please provide a concise professional summary (3-4 sentences) that includes:
1. The candidate's primary skills and experience
2. Actual years of experience.
3. Any notable strengths or gaps

Keep the summary professional and objective.
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical recruiter who provides concise, objective candidate assessments.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=200,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error generating AI summary: {str(e)}"

    def generate_batch_summaries(self, resumes: list) -> list:
        """
        Generate summaries for multiple resumes

        Args:
            resumes: List of resume data dictionaries

        Returns:
            List of resumes with AI summaries added
        """
        for resume in resumes:
            resume["ai_summary"] = self.generate_resume_summary(
                resume["text_content"],
                resume["keywords_found"],
                resume["keywords_missing"],
                resume["score"],
            )

        return resumes
