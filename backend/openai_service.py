import json
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
        Generate an AI summary of the resume and detect UAE presence

        Args:
            resume_text: Full text content of the resume
            keywords_found: List of keywords found in the resume
            keywords_missing: List of keywords missing from the resume
            score: Calculated keyword match score

        Returns:
            Dict with 'summary' (str) and 'uae_presence' (bool)
        """
        try:
            prompt = f"""
You are an expert recruiter analyzing a candidate's resume.

Resume Content:
{resume_text[:3000]}

Keyword Analysis:
- Match Score: {score}%
- Keywords Found: {", ".join(keywords_found) if keywords_found else "None"}
- Keywords Missing: {", ".join(keywords_missing) if keywords_missing else "None"}

Please analyze the resume and respond in the following JSON format:
{{
  "summary": "A concise professional summary (3-4 bullet points) covering: 1) Primary skills and experience, 2) Years of experience including UAE/Gulf experience, 3) Any notable strengths or gaps. Use bullet points separated by newlines.",
  "uae_presence": true or false
}}

For uae_presence, determine if the candidate appears to be currently located in the UAE by checking:
- Phone numbers starting with +971 or 00971
- Addresses or locations mentioning UAE, Dubai, Abu Dhabi, Sharjah, Ajman, Fujairah, Ras Al Khaimah, or Umm Al Quwain
- Most recent job location being in the UAE

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
                max_completion_tokens=300,
                temperature=0.7,
            )

            response_content = response.choices[0].message.content
            if response_content is None:
                return {
                    "summary": "Error: Empty response from AI",
                    "uae_presence": None,
                }

            response_text = response_content.strip()

            # Parse JSON response
            try:
                result = json.loads(response_text)
                return {
                    "summary": result.get("summary", ""),
                    "uae_presence": result.get("uae_presence", False),
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails - return the raw text as summary
                return {"summary": response_text, "uae_presence": None}

        except Exception as e:
            return {
                "summary": f"Error generating AI summary: {str(e)}",
                "uae_presence": None,
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
