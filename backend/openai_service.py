import json
from datetime import date
from openai import OpenAI
from typing import Dict, Any
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
    ) -> Dict[str, Any]:
        """
        Generate an AI summary of the resume, detect UAE presence, and extract employment history

        Args:
            resume_text: Full text content of the resume
            keywords_found: List of keywords found in the resume
            keywords_missing: List of keywords missing from the resume
            score: Calculated keyword match score

        Returns:
            Dict with 'summary' (str), 'uae_presence' (bool),
            'employment_history' (list), and 'total_experience_years' (float)
        """
        try:
            today = date.today().strftime("%B %d, %Y")
            prompt = f"""
You are an expert recruiter analyzing a candidate's resume.

Today's date is {today}.

Resume Content:
{resume_text[:6000]}

Keyword Analysis:
- Match Score: {score}%
- Keywords Found: {", ".join(keywords_found) if keywords_found else "None"}
- Keywords Missing: {", ".join(keywords_missing) if keywords_missing else "None"}

Please analyze the resume and respond in the following JSON format:
{{
  "summary": "A concise professional summary as a SINGLE STRING with 3-4 bullet points separated by newlines. Example: '• Point 1\\n• Point 2\\n• Point 3'. Cover: 1) Primary skills and experience, 2) Years of experience including UAE/Gulf experience, 3) Any notable strengths or gaps.",
  "uae_presence": true or false,
  "employment_history": [
    {{
      "company": "Company Name",
      "location": "City, Country or Country",
      "role": "Job Title",
      "start_date": "Mon YYYY",
      "end_date": "Mon YYYY or Present",
      "duration_years": 2.5
    }}
  ],
  "total_experience_years": 26.07
}}

Rules:
- For uae_presence, determine if the candidate appears to be currently located in the UAE by checking:
  - Phone numbers starting with +971 or 00971
  - Addresses or locations mentioning UAE, Dubai, Abu Dhabi, Sharjah, Ajman, Fujairah, Ras Al Khaimah, or Umm Al Quwain
  - Most recent job location being in the UAE
- For employment_history, extract ALL positions from the resume in reverse chronological order (most recent first). Do NOT skip or combine positions. Every distinct role must be its own entry.
  - Calculate duration_years as the difference in years between start and end dates, rounded to 2 decimal places.
  - If a position is current/ongoing, use "Present" as end_date and calculate duration from start_date to today's date ({today}).
  - If location is not clear, use "Not specified".
- For total_experience_years, sum all the duration_years values, rounded to 2 decimal places.

Respond ONLY with valid JSON, no additional text or markdown formatting.
"""

            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical recruiter who provides concise, objective candidate assessments. Always respond with valid JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=2500,
                temperature=0.4,
            )

            response_content = response.choices[0].message.content
            if response_content is None:
                return {
                    "summary": "Error: Empty response from AI",
                    "uae_presence": None,
                    "employment_history": None,
                    "total_experience_years": None,
                }

            response_text = response_content.strip()

            # Parse JSON response
            try:
                result = json.loads(response_text)
                summary = result.get("summary", "")
                # Handle case where OpenAI returns summary as a list instead of string
                if isinstance(summary, list):
                    summary = "\n".join(str(item) for item in summary)
                return {
                    "summary": summary,
                    "uae_presence": result.get("uae_presence", False),
                    "employment_history": result.get("employment_history"),
                    "total_experience_years": result.get("total_experience_years"),
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails - return the raw text as summary
                return {
                    "summary": response_text,
                    "uae_presence": None,
                    "employment_history": None,
                    "total_experience_years": None,
                }

        except Exception as e:
            return {
                "summary": f"Error generating AI summary: {str(e)}",
                "uae_presence": None,
                "employment_history": None,
                "total_experience_years": None,
            }

    def generate_batch_summaries(self, resumes: list) -> list:
        """
        Generate summaries for multiple resumes

        Args:
            resumes: List of resume data dictionaries

        Returns:
            List of resumes with AI summaries and UAE presence added
        """
        for resume in resumes:
            result = self.generate_resume_summary(
                resume["text_content"],
                resume["keywords_found"],
                resume["keywords_missing"],
                resume["score"],
            )
            resume["ai_summary"] = result.get("summary")
            resume["uae_presence"] = result.get("uae_presence")

        return resumes
