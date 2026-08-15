import re
import unicodedata
from typing import Any, Dict, List, Optional

# Attempt to import TextNormalizer with graceful fallback if unavailable
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
    - Text normalization (Unicode NFKC, lowercase, whitespace trimming)
    - Fallback integration with external TextNormalizer
    - Grouped exact string pattern matching
    - Grouped regex pattern matching
    - Fault-tolerant execution preventing fuzzing campaign crashes
    """

    def __init__(self):
        # Initialize custom normalizer if present in the environment
        self.normalizer = TextNormalizer() if TextNormalizer else None

    def normalize(self, text: Any) -> str:
        """
        Safely normalize arbitrary input into a standardized string format.
        
        Applies Unicode NFKC normalization, lowercase conversion, and collapses
        consecutive whitespace characters.
        """
        if text is None:
            return ""

        try:
            # Prefer custom TextNormalizer if available and implemented
            if self.normalizer and hasattr(self.normalizer, "normalize"):
                normalized_val = self.normalizer.normalize(text)
                if normalized_val is not None:
                    return str(normalized_val)

            # Standard built-in normalization pipeline
            text = str(text)
            text = unicodedata.normalize("NFKC", text)
            text = text.lower()
            text = re.sub(r"\s+", " ", text)  # Collapse repeated whitespace
            return text.strip()

        except Exception:
            # Fallback to empty string on unexpected conversion error
            return ""

    def find_patterns(
        self,
        text: Any,
        patterns: Optional[Dict[str, List[str]]] = None,
        pattern_groups: Optional[Dict[str, List[str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search grouped string patterns against target text and return match evidence.
        
        Accepts patterns via either 'patterns' or 'pattern_groups' parameter names
        for backward compatibility. Never raises exceptions to caller.
        """
        results = []

        try:
            # Resolve argument name alias (supports patterns or pattern_groups)
            target_patterns = patterns if patterns is not None else pattern_groups

            if not isinstance(target_patterns, dict):
                return results

            # Normalize incoming target text
            normalized = self.normalize(text)
            if not normalized:
                return results

            # Iterate through pattern groups
            for group_name, group_patterns in target_patterns.items():

                if not isinstance(group_patterns, list):
                    continue

                for pattern in group_patterns:

                    try:
                        if pattern is None:
                            continue

                        # Convert pattern to string and normalize
                        pattern_str = str(pattern).strip()
                        pattern_normalized = self.normalize(pattern_str)

                        if not pattern_normalized:
                            continue

                        # Check if substring exists within normalized target text
                        if pattern_normalized in normalized:
                            results.append({
                                "group": group_name,
                                "pattern": pattern_str,
                                "type": "string"
                            })

                    except Exception:
                        # Malformed individual pattern should not halt processing
                        continue

            return results

        except Exception:
            # Prevent Oracle failures from interrupting the fuzzing campaign
            return []

    def find_regex_patterns(
        self,
        text: Any,
        patterns: Optional[Dict[str, List[str]]] = None,
        pattern_groups: Optional[Dict[str, List[str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search grouped regex patterns against target text and return match evidence.
        
        Accepts patterns via either 'patterns' or 'pattern_groups' parameter names.
        Ignores invalid regex expressions gracefully.
        """
        results = []

        try:
            # Resolve argument name alias
            target_patterns = patterns if patterns is not None else pattern_groups

            if not isinstance(target_patterns, dict):
                return results

            # Normalize incoming target text
            normalized = self.normalize(text)
            if not normalized:
                return results

            # Iterate through pattern groups
            for group_name, regex_patterns in target_patterns.items():

                if not isinstance(regex_patterns, list):
                    continue

                for pattern in regex_patterns:

                    try:
                        if not isinstance(pattern, str):
                            continue

                        # Execute case-insensitive regex match on normalized text
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
                        # Catch invalid regex syntax and continue evaluation
                        continue

                    except Exception:
                        continue

            return results

        except Exception:
            # Safe boundary for the Oracle engine
            return []