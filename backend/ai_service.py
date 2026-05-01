import json
import re
from datetime import date
from typing import Any, Dict

from ai_providers import AIProviderError, build_provider_chain
from config import settings


SYSTEM_INSTRUCTION = (
    "You are an expert technical recruiter who provides concise, objective "
    "candidate assessments. Always respond with valid JSON only."
)


class AIService:
    """
    Service for generating AI summaries of resumes.

    Uses a configurable provider chain (Gemini -> Groq -> OpenRouter by
    default). Each provider is tried in order; on transient failures the
    next provider is used. Public API is unchanged from the single-provider
    implementation so callers in main.py do not need to be modified.
    """

    def __init__(self):
        self.providers = build_provider_chain(settings)
        if not self.providers:
            raise ValueError(
                "No AI provider is configured. Please set GEMINI_API_KEY, "
                "GROQ_API_KEY, or OPENROUTER_API_KEY in your .env file."
            )
        names = ", ".join(p.name for p in self.providers)
        print(f"[ai] provider chain: {names}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_resume_summary(
        self,
        resume_text: str,
        keywords_found: list,
        keywords_missing: list,
        score: int,
    ) -> Dict[str, Any]:
        """
        Generate an AI summary of the resume, detect UAE presence, and extract
        employment history.

        Returns a dict with keys ``summary``, ``uae_presence``,
        ``employment_history``, and ``total_experience_years``. On total
        failure, ``summary`` will contain a human-readable error string and
        the other fields will be ``None``.
        """
        prompt = self._build_prompt(
            resume_text, keywords_found, keywords_missing, score
        )

        last_error: Exception | None = None
        for provider in self.providers:
            try:
                raw = provider.generate_json(
                    system=SYSTEM_INSTRUCTION,
                    prompt=prompt,
                    max_tokens=5000,
                    temperature=0.4,
                )
                return self._parse_response(raw)
            except AIProviderError as exc:
                last_error = exc
                print(f"[ai] provider {provider.name} failed, trying next: {exc}")
                continue
            except Exception as exc:  # noqa: BLE001
                # Defensive: never let a provider bug crash the request.
                last_error = exc
                print(f"[ai] provider {provider.name} unexpected error: {exc}")
                continue

        return {
            "summary": (f"AI summary unavailable (all providers failed: {last_error})"),
            "uae_presence": None,
            "employment_history": None,
            "total_experience_years": None,
        }

    def generate_batch_summaries(self, resumes: list) -> list:
        """Generate summaries for multiple resumes."""
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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(
        resume_text: str,
        keywords_found: list,
        keywords_missing: list,
        score: int,
    ) -> str:
        today = date.today().strftime("%B %d, %Y")
        return f"""
You are an expert recruiter analyzing a candidate's resume.

Today's date is {today}.

Resume Content:
{resume_text[:50000]}

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
      "duration_years": 0.0
    }}
  ],
  "total_experience_years": 0.0
}}

Rules:
- For uae_presence, determine if the candidate appears to be currently located in the UAE by checking:
  - Phone numbers starting with +971 or 00971
  - Addresses or locations mentioning UAE, Dubai, Abu Dhabi, Sharjah, Ajman, Fujairah, Ras Al Khaimah, or Umm Al Quwain
  - Most recent job location being in the UAE
- IMPORTANT: For employment_history, first count ALL distinct job positions listed in the resume, then extract EVERY SINGLE ONE in reverse chronological order (most recent first). Do NOT skip, merge, or combine any positions. If the resume lists 7 jobs, the array MUST have exactly 7 entries.
  - Calculate duration_years as the difference in years between start and end dates, rounded to 2 decimal places.
  - If a position is current/ongoing, use "Present" as end_date and calculate duration from start_date to today's date ({today}).
  - If location is not clear, use "Not specified".
- For total_experience_years, sum all the duration_years values, rounded to 2 decimal places.

Respond ONLY with valid JSON, no additional text or markdown formatting.
"""

    @staticmethod
    def _parse_response(raw: str) -> Dict[str, Any]:
        """Normalize a raw model response into the expected dict shape."""
        response_text = (raw or "").strip()

        # Strip markdown JSON fences if present (e.g. ```json ... ```)
        if response_text.startswith("```"):
            response_text = re.sub(r"^```(?:json)?\s*\n?", "", response_text)
            response_text = re.sub(r"\n?```\s*$", "", response_text)
            response_text = response_text.strip()

        print(f"[ai] raw response (first 500 chars): {response_text[:500]}")

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as exc:
            print(f"[ai] JSON parse error: {exc}")
            print(f"[ai] full response that failed parsing: {response_text}")
            return {
                "summary": response_text,
                "uae_presence": None,
                "employment_history": None,
                "total_experience_years": None,
            }

        summary = result.get("summary", "")
        # Defensive: some models return summary as a list of bullets
        if isinstance(summary, list):
            summary = "\n".join(str(item) for item in summary)

        history = result.get("employment_history")
        total_years = result.get("total_experience_years")
        print(
            f"[ai] employment entries: {len(history) if history else 0}, "
            f"total years: {total_years}"
        )

        return {
            "summary": summary,
            "uae_presence": result.get("uae_presence", False),
            "employment_history": history,
            "total_experience_years": total_years,
        }
