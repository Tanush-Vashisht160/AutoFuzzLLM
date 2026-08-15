import re
import unicodedata
from typing import Any, Dict, List

try:
    from fuzzing.oracle.normalizer import TextNormalizer
except ImportError:
    try:
        from fuzzing.oracle.normalizer import TextNormalizer
    except ImportError:
        TextNormalizer = None


class PatternEngine:
    """
    Centralized pattern matching engine.

    Handles:
    - Unicode normalization
    - Lowercase normalization
    - Whitespace normalization
    - Repeated whitespace handling
    - Exact regex pattern matching
    - String substring pattern matching
    """

    def __init__(self):
        self.normalizer = TextNormalizer() if TextNormalizer else None

    def normalize(self, text: Any) -> str:
        """
        Safely normalize arbitrary detector input.
        """
        if text is None:
            return ""

        try:
            if self.normalizer and hasattr(self.normalizer, "normalize"):
                normalized_val = self.normalizer.normalize(text)
                if normalized_val is not None:
                    return str(normalized_val)

            text = str(text)
            text = unicodedata.normalize("NFKC", text)
            text = text.lower()
            text = re.sub(r"\s+", " ", text)
            return text.strip()

        except Exception:
            return ""

    def find_patterns(
        self,
        text: Any,
        patterns: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Search grouped string patterns and return evidence.

        Never raises an exception to the caller.
        """
        results = []

        try:
            if not isinstance(patterns, dict):
                return results

            normalized = self.normalize(text)

            if not normalized:
                return results

            for group_name, group_patterns in patterns.items():

                if not isinstance(group_patterns, list):
                    continue

                for pattern in group_patterns:

                    try:
                        if not isinstance(pattern, str):
                            continue

                        pattern_normalized = self.normalize(pattern)

                        if not pattern_normalized:
                            continue

                        if pattern_normalized in normalized:
                            results.append({
                                "group": group_name,
                                "pattern": pattern,
                                "type": "string"
                            })

                    except Exception:
                        # One bad pattern should never stop the campaign.
                        continue

            return results

        except Exception:
            # Oracle should never crash the fuzzing campaign.
            return []

    def find_regex_patterns(
        self,
        text: Any,
        patterns: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Search grouped regex patterns and return evidence.

        Never raises an exception to the caller.
        """
        results = []

        try:
            if not isinstance(patterns, dict):
                return results

            normalized = self.normalize(text)

            if not normalized:
                return results

            for group_name, regex_patterns in patterns.items():

                if not isinstance(regex_patterns, list):
                    continue

                for pattern in regex_patterns:

                    try:
                        if not isinstance(pattern, str):
                            continue

                        match = re.search(
                            pattern,
                            normalized,
                            flags=re.IGNORECASE
                        )

                        if match:
                            results.append({
                                "group": group_name,
                                "pattern": pattern,
                                "type": "regex",
                                "match": match.group(0)
                            })

                    except re.error:
                        # Invalid regex should not kill the campaign.
                        continue

                    except Exception:
                        continue

            return results

        except Exception:
            return []