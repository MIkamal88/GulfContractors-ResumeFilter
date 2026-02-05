import pandas as pd
from typing import List
from models import ResumeAnalysis
import io


class CSVExporter:
    """
    Exports filtered resume data to CSV format
    """

    @staticmethod
    def export_to_csv_buffer(candidates: List[ResumeAnalysis]) -> io.StringIO:
        """
        Export candidate data to CSV in-memory buffer

        Args:
            candidates: List of ResumeAnalysis objects

        Returns:
            StringIO buffer containing CSV data
        """
        # Convert candidates to DataFrame
        data = []
        for candidate in candidates:
            # Convert uae_presence to human-readable string
            if candidate.uae_presence is None:
                uae_status = "N/A"
            elif candidate.uae_presence:
                uae_status = "Yes"
            else:
                uae_status = "No"

            # Handle image-based resumes
            if candidate.is_image_based:
                score_display = "N/A (Image-based)"
                ai_summary = "Could not process - resume appears to be image-based"
            else:
                score_display = str(candidate.score)
                ai_summary = candidate.ai_summary or "N/A"

            # Format employment history for CSV
            if candidate.employment_history:
                history_lines = []
                for i, entry in enumerate(candidate.employment_history, 1):
                    history_lines.append(
                        f"{i}- {entry.company} - {entry.location} - "
                        f"{entry.role} ({entry.start_date} - {entry.end_date}) "
                        f"[{entry.duration_years} yrs]"
                    )
                if candidate.total_experience_years is not None:
                    history_lines.append(
                        f"Total: {candidate.total_experience_years} years"
                    )
                employment_history = "\n".join(history_lines)
            else:
                employment_history = "N/A"

            total_exp = (
                str(candidate.total_experience_years)
                if candidate.total_experience_years is not None
                else "N/A"
            )

            data.append(
                {
                    "Filename": candidate.filename,
                    "Score": score_display,
                    "UAE Presence": uae_status,
                    "Total Experience (Years)": total_exp,
                    "Keywords Found": ", ".join(candidate.keywords_found),
                    "Keywords Missing": ", ".join(candidate.keywords_missing),
                    "AI Summary": ai_summary,
                    "Employment History": employment_history,
                    "Parsed At": candidate.parsed_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        df = pd.DataFrame(data)

        # Sort by score (highest first)
        df = df.sort_values("Score", ascending=False)

        # Export to CSV buffer
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8")
        csv_buffer.seek(0)

        return csv_buffer
