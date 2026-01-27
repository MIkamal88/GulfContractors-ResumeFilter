from typing import List, Tuple, Set, Optional
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
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def get_word_variations(word: str) -> Set[str]:
        """
        Generate common variations of a word (plural/singular forms)

        Args:
            word: Base word to generate variations for

        Returns:
            Set of word variations including the original
        """
        word = word.lower().strip()
        variations = {word}

        # If word ends with common plural suffixes, add singular form
        if word.endswith("ies") and len(word) > 3:
            # e.g., "batteries" -> "battery"
            variations.add(word[:-3] + "y")
        elif word.endswith("es"):
            if (
                word.endswith("sses")
                or word.endswith("shes")
                or word.endswith("ches")
                or word.endswith("xes")
                or word.endswith("zes")
            ):
                # e.g., "boxes" -> "box", "watches" -> "watch"
                variations.add(word[:-2])
            elif word.endswith("ves") and len(word) > 3:
                # e.g., "valves" -> "valve", but also try "knives" -> "knife"
                variations.add(word[:-1])  # "valves" -> "valve"
                variations.add(word[:-3] + "f")  # "knives" -> "knife"
                variations.add(word[:-3] + "fe")  # "wives" -> "wife"
            else:
                # e.g., "cranes" -> "crane" (remove just 's'), "buses" -> "bus" (remove 'es')
                variations.add(word[:-1])
                variations.add(word[:-2])
        elif word.endswith("s") and not word.endswith("ss"):
            # Simple plural: e.g., "cranes" -> "crane", "operators" -> "operator"
            variations.add(word[:-1])

        # If word is singular, add common plural forms
        if word.endswith("y") and len(word) > 2 and word[-2] not in "aeiou":
            # e.g., "battery" -> "batteries"
            variations.add(word[:-1] + "ies")
        elif word.endswith(("s", "sh", "ch", "x", "z")):
            # e.g., "box" -> "boxes", "watch" -> "watches"
            variations.add(word + "es")
        elif word.endswith("f"):
            # e.g., "leaf" -> "leaves"
            variations.add(word[:-1] + "ves")
        elif word.endswith("fe"):
            # e.g., "knife" -> "knives"
            variations.add(word[:-2] + "ves")

        # Always add simple 's' plural
        if not word.endswith("s"):
            variations.add(word + "s")

        return variations

    @staticmethod
    def generate_phrase_patterns(phrase: str) -> List[str]:
        """
        Generate regex patterns for a phrase, handling variations of each word

        Args:
            phrase: Keyword phrase (single word or multi-word)

        Returns:
            List of regex patterns to match
        """
        words = phrase.split()

        if len(words) == 1:
            # Single word: generate variations
            variations = KeywordMatcher.get_word_variations(words[0])
            return [r"\b" + re.escape(v) + r"\b" for v in variations]
        else:
            # Multi-word phrase: generate variations for each word and combine
            word_variation_sets = [KeywordMatcher.get_word_variations(w) for w in words]

            # For phrases, just use variations of the last word (most common for plurals)
            # e.g., "tower crane" should match "tower cranes"
            patterns = []

            # Original phrase
            patterns.append(r"\b" + r"\s+".join(re.escape(w) for w in words) + r"\b")

            # Phrase with last word variations
            for variation in word_variation_sets[-1]:
                if variation != words[-1]:
                    phrase_words = words[:-1] + [variation]
                    patterns.append(
                        r"\b" + r"\s+".join(re.escape(w) for w in phrase_words) + r"\b"
                    )

            return patterns

    @staticmethod
    def find_keywords(text: str, keywords: List[str]) -> Tuple[List[str], List[str]]:
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

            # Generate patterns for the keyword and its variations
            patterns = KeywordMatcher.generate_phrase_patterns(normalized_keyword)

            # Check if any variation matches
            keyword_found = False
            for pattern in patterns:
                if re.search(pattern, normalized_text):
                    keyword_found = True
                    break

            if keyword_found:
                found.append(keyword)
            else:
                missing.append(keyword)

        return found, missing

    @staticmethod
    def calculate_score(
        found_keywords: List[str],
        all_keywords: List[str],
        double_weight_keywords: Optional[List[str]] = None,
    ) -> int:
        """
        Calculate percentage score based on keywords found with weight support

        Args:
            found_keywords: List of keywords found in resume
            all_keywords: List of all keywords to search for
            double_weight_keywords: List of keywords that count as 2x weight

        Returns:
            Score as percentage (0-100)
        """
        if len(all_keywords) == 0:
            return 0

        if double_weight_keywords is None:
            double_weight_keywords = []

        # Normalize double_weight_keywords for comparison
        double_weight_set = {kw.lower().strip() for kw in double_weight_keywords}

        # Calculate total possible weight
        # Regular keywords = 1 point each, double-weight keywords = 2 points each
        total_weight = 0
        for kw in all_keywords:
            if kw.lower().strip() in double_weight_set:
                total_weight += 2  # Double-weight keyword worth 2 points
            else:
                total_weight += 1  # Regular keyword worth 1 point

        # Calculate found weight
        found_weight = 0
        for kw in found_keywords:
            if kw.lower().strip() in double_weight_set:
                found_weight += 2  # Double-weight keyword found
            else:
                found_weight += 1  # Regular keyword found

        score = (found_weight / total_weight) * 100
        return int(score)

    @staticmethod
    def analyze_resume(
        text: str,
        keywords: List[str],
        double_weight_keywords: Optional[List[str]] = None,
    ) -> Tuple[List[str], List[str], int]:
        """
        Complete analysis of resume against keywords with weight support

        Args:
            text: Resume text content
            keywords: List of keywords to match
            double_weight_keywords: List of keywords that count as 2x weight

        Returns:
            Tuple of (found_keywords, missing_keywords, score)
        """
        if double_weight_keywords is None:
            double_weight_keywords = []

        found, missing = KeywordMatcher.find_keywords(text, keywords)
        score = KeywordMatcher.calculate_score(found, keywords, double_weight_keywords)

        return found, missing, score
