from typing import Any, Dict


def safe_detect(detector, text: str) -> Dict[str, Any]:
    """
    Safely execute an Oracle detector.

    Guarantees a consistent result structure even if:
    - detector crashes
    - detector returns None
    - detector returns a non-dict
    - detector uses 'keywords' instead of 'matched_keywords'
    - detector uses 'refused' instead of 'success'
    """

    base_result = {
        "success": False,
        "score": 0.0,
        "confidence": 0.0,
        "category": "Unknown",
        "matched_keywords": [],
        "refused": False,
        "error": None,
    }

    try:
        if detector is None:
            base_result["error"] = "Detector is None"
            return base_result

        if not hasattr(detector, "detect"):
            base_result["error"] = "Detector has no detect() method"
            return base_result

        result = detector.detect(text)

        if not isinstance(result, dict):
            base_result["error"] = (
                f"Detector returned {type(result).__name__}, expected dict"
            )
            return base_result

        # Normalize success
        success = result.get("success", False)

        # Refusal detector uses "refused"
        refused = bool(result.get("refused", False))

        if "success" not in result and refused:
            success = False

        # Normalize keywords
        keywords = result.get(
            "matched_keywords",
            result.get("keywords", [])
        )

        if keywords is None:
            keywords = []

        if not isinstance(keywords, list):
            keywords = [str(keywords)]

        # Normalize score
        try:
            score = float(result.get("score", 0.0))
        except (TypeError, ValueError):
            score = 0.0

        # Normalize confidence
        try:
            confidence = float(result.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0

        confidence = max(0.0, min(1.0, confidence))

        # Category
        category = result.get(
            "category",
            getattr(detector, "CATEGORY", "Unknown")
        )

        normalized = {
            "success": bool(success),
            "score": max(0.0, score),
            "confidence": confidence,
            "category": category,
            "matched_keywords": keywords,
            "refused": refused,
            "error": result.get("error"),
        }

        return normalized

    except Exception as exc:
        base_result["error"] = f"{type(exc).__name__}: {exc}"
        return base_result