from typing import List, Tuple
import re


class KeywordMatcher:
    """
    Matches and scores resumes based on keyword presence
    """

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for better keyword matching

        Args:
            text: Input text

        Returns:
            Normalized text (lowercase, extra spaces removed)
        """
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def find_keywords(
        text: str,
        keywords: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Find which keywords are present in the text

        Args:
            text: Resume text content
            keywords: List of keywords to search for

        Returns:
            Tuple of (found_keywords, missing_keywords)
        """
        normalized_text = KeywordMatcher.normalize_text(text)
        found = []
        missing = []

        for keyword in keywords:
            normalized_keyword = KeywordMatcher.normalize_text(keyword)

            # Check for whole word match or phrase match
            pattern = r'\b' + re.escape(normalized_keyword) + r'\b'
            if re.search(pattern, normalized_text):
                found.append(keyword)
            else:
                missing.append(keyword)

        return found, missing

    @staticmethod
    def calculate_score(
        found_keywords: List[str],
        total_keywords: int
    ) -> int:
        """
        Calculate percentage score based on keywords found

        Args:
            found_keywords: List of keywords found in resume
            total_keywords: Total number of keywords to search for

        Returns:
            Score as percentage (0-100)
        """
        if total_keywords == 0:
            return 0

        score = (len(found_keywords) / total_keywords) * 100
        return int(score)

    @staticmethod
    def analyze_resume(
        text: str,
        keywords: List[str]
    ) -> Tuple[List[str], List[str], int]:
        """
        Complete analysis of resume against keywords

        Args:
            text: Resume text content
            keywords: List of keywords to match

        Returns:
            Tuple of (found_keywords, missing_keywords, score)
        """
        found, missing = KeywordMatcher.find_keywords(text, keywords)
        score = KeywordMatcher.calculate_score(found, len(keywords))

        return found, missing, score
