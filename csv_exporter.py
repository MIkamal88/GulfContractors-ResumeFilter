import pandas as pd
from typing import List, Optional
from models import ResumeAnalysis
import os
from datetime import datetime


class CSVExporter:
    """
    Exports filtered resume data to CSV format
    """

    @staticmethod
    def ensure_output_directory(file_path: str):
        """
        Ensure the output directory exists

        Args:
            file_path: Full path to the output file
        """
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def export_to_csv(
        candidates: List[ResumeAnalysis],
        output_path: str,
        resume_folder_path: Optional[str] = None,
    ) -> str:
        """
        Export candidate data to CSV file with optional Excel hyperlinks

        Args:
            candidates: List of ResumeAnalysis objects
            output_path: Path where CSV should be saved
            resume_folder_path: Optional path to folder containing resumes.
                              If provided, filenames will be converted to Excel HYPERLINK formulas

        Returns:
            Path to the created CSV file
        """
        # Ensure output directory exists
        CSVExporter.ensure_output_directory(output_path)

        # Convert candidates to DataFrame
        data = []
        for candidate in candidates:
            # Create filename entry (with hyperlink if resume_folder_path is provided)
            if resume_folder_path:
                # Create absolute path to resume file
                resume_file_path = os.path.join(resume_folder_path, candidate.filename)
                resume_file_path = os.path.abspath(resume_file_path)

                # Convert to file:// URL format (works in Excel)
                # Excel needs forward slashes even on Windows
                file_url = resume_file_path.replace("\\", "/")

                # Create Excel HYPERLINK formula
                filename_cell = (
                    f'=HYPERLINK("file:///{file_url}","{candidate.filename}")'
                )
            else:
                filename_cell = candidate.filename

            data.append(
                {
                    "Filename": filename_cell,
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

        # Export to CSV
        df.to_csv(output_path, index=False, encoding="utf-8")

        return output_path

    @staticmethod
    def create_timestamped_path(base_path: str) -> str:
        """
        Create a timestamped version of the output path

        Args:
            base_path: Base path for the CSV file

        Returns:
            Timestamped path
        """
        directory = os.path.dirname(base_path)
        filename = os.path.basename(base_path)
        name, ext = os.path.splitext(filename)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_filename = f"{name}_{timestamp}{ext}"

        return os.path.join(directory, timestamped_filename)


