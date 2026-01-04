import PyPDF2
import docx
import io
from typing import Tuple


# Minimum character threshold to consider text extraction successful
MIN_TEXT_LENGTH = 100


class ResumeParser:
    """
    Parser for extracting text from resume files (PDF and DOCX formats)
    """

    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        """
        Extract text from PDF file

        Args:
            file_content: Raw bytes of the PDF file

        Returns:
            Extracted text content
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")

    @staticmethod
    def parse_docx(file_content: bytes) -> str:
        """
        Extract text from DOCX file

        Args:
            file_content: Raw bytes of the DOCX file

        Returns:
            Extracted text content
        """
        try:
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)

            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {str(e)}")

    @staticmethod
    def parse_resume(filename: str, file_content: bytes) -> Tuple[str, bool]:
        """
        Parse resume based on file extension

        Args:
            filename: Name of the file
            file_content: Raw bytes of the file

        Returns:
            Tuple of (extracted text content, is_image_based flag)
            is_image_based is True if the resume appears to be mostly images
            (less than MIN_TEXT_LENGTH characters extracted)

        Raises:
            ValueError: If file format is not supported
        """
        filename_lower = filename.lower()

        if filename_lower.endswith(".pdf"):
            text = ResumeParser.parse_pdf(file_content)
        elif filename_lower.endswith(".docx"):
            text = ResumeParser.parse_docx(file_content)
        else:
            raise ValueError("Unsupported file format. Supported formats: PDF, DOCX")

        # Check if resume is image-based (too little text extracted)
        is_image_based = len(text) < MIN_TEXT_LENGTH

        return text, is_image_based
