import re
import unicodedata


class TextNormalizer:

    @staticmethod
    def normalize(text: str) -> str:
        """
        Basic normalization for Oracle pattern matching.

        Does NOT blindly decode arbitrary content.
        """

        if text is None:
            return ""

        if not isinstance(text, str):
            text = str(text)

        # Unicode normalization
        text = unicodedata.normalize("NFKC", text)

        # Lowercase
        text = text.lower()

        # Normalize common whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove zero-width characters
        text = re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]", "", text)

        # Normalize repeated punctuation/characters
        text = re.sub(r"(.)\1{3,}", r"\1\1", text)

        return text.strip()

    @staticmethod
    def compact(text: str) -> str:
        """
        More aggressive representation useful for
        detecting spaced-out phrases.
        """

        text = TextNormalizer.normalize(text)

        # Remove spaces between characters.
        compacted = re.sub(r"\s+", "", text)

        return compacted