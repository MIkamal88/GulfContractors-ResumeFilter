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
            data.append(
                {
                    "Filename": candidate.filename,
                    "Score": candidate.score,
                    "Keywords Found": ", ".join(candidate.keywords_found),
                    "Keywords Missing": ", ".join(candidate.keywords_missing),
                    "AI Summary": candidate.ai_summary or "N/A",
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
