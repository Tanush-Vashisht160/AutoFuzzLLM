"""
AutoFuzzLLM - FastAPI Backend
--------------------------------

This file connects the new HTML/CSS/JavaScript frontend
to the existing AutoFuzzLLM Python fuzzing engine.

Architecture:

Browser
   ↓
FastAPI
   ↓
FuzzCampaign
   ↓
FuzzExecutor
   ↓
LLMRouter
   ↓
LLM Provider
"""

from pathlib import Path
from typing import Optional, List, Any
import math
import traceback

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# ------------------------------------------------------------
# Existing AutoFuzzLLM components
# ------------------------------------------------------------

from fuzzing.campaign import FuzzCampaign
from analysis.risk_score import RiskScorer
from analysis.response_classifier import ResponseClassifier
from analysis.owasp_mapper import OWASPMapper


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
# ============================================================
# FRONTEND CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

INDEX_FILE = FRONTEND_DIR / "index.html"
CSS_FILE = FRONTEND_DIR / "components.css"
JS_FILE = FRONTEND_DIR / "app.js"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AutoFuzzLLM API",
    description="Backend API for the AutoFuzzLLM security fuzzing platform.",
    version="1.0.0",
)

# ============================================================
# FRONTEND VALIDATION
# ============================================================

@app.on_event("startup")
async def validate_frontend():

    print("\n" + "=" * 60)
    print("AutoFuzzLLM Frontend Validation")
    print("=" * 60)

    print(f"Frontend directory : {FRONTEND_DIR}")
    print(f"Directory exists   : {FRONTEND_DIR.exists()}")

    if not FRONTEND_DIR.exists():
        print(
            f"[ERROR] Frontend directory does not exist:\n"
            f"{FRONTEND_DIR}"
        )
        return

    required_files = {
        "index.html": INDEX_FILE,
        "components.css": CSS_FILE,
        "app.js": JS_FILE,
    }

    for name, path in required_files.items():

        if path.exists():
            print(f"[OK] {name}")
        else:
            print(
                f"[ERROR] Missing {name}: {path}"
            )

    print("=" * 60 + "\n")
# ============================================================
# ANALYSIS ENGINES
# ============================================================

risk_scorer = RiskScorer()
classifier = ResponseClassifier()
owasp_mapper = OWASPMapper()


# ============================================================
# REQUEST MODELS
# ============================================================

class CampaignRequest(BaseModel):
    """
    Configuration received from the JavaScript frontend.
    """

    providers: List[str] = Field(
        default=["Phi3 Mini"],
        min_length=1,
    )

    seed_source: str = "Custom Prompt"

    dataset_name: Optional[str] = None

    custom_prompt: str = ""

    initial_seed_count: int = Field(
        default=100,
        ge=1,
        le=500,
    )

    mutations: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    generations: int = Field(
        default=3,
        ge=1,
        le=10,
    )

    seed_pool_size: int = Field(
        default=100,
        ge=10,
        le=500,
    )

    fitness_threshold: float = Field(
        default=30,
        ge=0,
        le=100,
    )


class ConversationRequest(BaseModel):
    provider: str = "Phi3 Mini"
    messages: List[dict] = Field(default_factory=list)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def safe_number(value: Any, default: float = 0) -> float:
    """
    Converts numbers safely for JSON responses.

    Prevents NaN / Infinity from breaking the frontend.
    """

    try:
        number = float(value)

        if not math.isfinite(number):
            return default

        return number

    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely converts a value into an integer.
    """

    try:
        return int(value)

    except (TypeError, ValueError):
        return default


def normalize_dataset_name(dataset_name: Optional[str]) -> Optional[str]:
    """
    The Streamlit UI historically uses:

        Benchmark Dataset 1
        Benchmark Dataset 2

    while ArtifactLoader may expect:

        Dataset 1
        Dataset 2

    Normalize both formats here so the frontend can remain readable.
    """

    if not dataset_name:
        return None

    mapping = {
        "Benchmark Dataset 1": "Dataset 1",
        "Benchmark Dataset 2": "Dataset 2",
        "Dataset 1": "Dataset 1",
        "Dataset 2": "Dataset 2",
    }

    return mapping.get(
        dataset_name,
        dataset_name,
    )


def serialize_result(result: dict) -> dict:
    """
    Converts one campaign result into JSON-safe frontend data.
    """

    if not isinstance(result, dict):
        return {
            "provider": "Unknown",
            "severity": "Failed",
            "status": "Infrastructure Error",
            "prompt": "",
            "response": "",
            "reason": "Invalid result returned by campaign engine.",
            "score": 0,
            "lvi_score": 0,
            "lvi_level": "N/A",
            "response_time": 0,
            "attack_category": "Unknown",
            "mutation_category": "Unknown",
            "owasp": "Unknown",
        }

    response_text = result.get("response", "")

    if not isinstance(response_text, str):
        response_text = str(response_text)

    prompt = result.get("prompt", "")

    if not isinstance(prompt, str):
        prompt = str(prompt)

    severity = result.get(
        "severity",
        "Failed",
    )

    status = result.get(
        "status",
        "Unknown",
    )

    attack_category = result.get(
        "attack_category",
        "Unknown",
    )

    mutation_category = result.get(
        "mutation_category",
        "Unknown",
    )

    # --------------------------------------------------------
    # Risk score
    # --------------------------------------------------------

    try:
        risk_data = risk_scorer.score(response_text)

    except Exception:
        risk_data = {
            "score": 0
        }

    risk_score = safe_number(
        risk_data.get("score", 0)
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    try:
        classification = classifier.classify(
            response_text
        )

    except Exception:
        classification = "Unknown"

    # --------------------------------------------------------
    # OWASP mapping
    # --------------------------------------------------------

    try:
        owasp = owasp_mapper.get_category(
            attack_category
        )

    except Exception:
        owasp = "Unknown"

    # --------------------------------------------------------
    # LVI
    # --------------------------------------------------------

    lvi_score = safe_number(
        result.get("lvi_score", 0)
    )

    # --------------------------------------------------------
    # Response length
    # --------------------------------------------------------

    response_length = len(
        response_text.split()
    )

    return {
        "provider": str(
            result.get("provider", "Unknown")
        ),

        "generation": safe_int(
            result.get("generation", 0)
        ),

        "mutation_category": str(
            mutation_category
        ),

        "attack_category": str(
            attack_category
        ),

        "owasp": str(
            owasp
        ),

        "prompt": prompt,

        "response": response_text,

        "response_summary": str(
            result.get(
                "response_summary",
                response_text[:500],
            )
        ),

        "reason": str(
            result.get(
                "reason",
                "",
            )
        ),

        "score": risk_score,

        "lvi_score": lvi_score,

        "lvi_level": str(
            result.get(
                "lvi_level",
                "N/A",
            )
        ),

        "lvi_rating": str(
            result.get(
                "lvi_rating",
                "N/A",
            )
        ),

        "lvi_severity": safe_number(
            result.get(
                "lvi_severity",
                0,
            )
        ),

        "lvi_exploitability": safe_number(
            result.get(
                "lvi_exploitability",
                0,
            )
        ),

        "lvi_confidence": safe_number(
            result.get(
                "lvi_confidence",
                0,
            )
        ),

        "lvi_novelty": safe_number(
            result.get(
                "lvi_novelty",
                0,
            )
        ),

        "lvi_reproducibility": safe_number(
            result.get(
                "lvi_reproducibility",
                0,
            )
        ),

        "lvi_impact": safe_number(
            result.get(
                "lvi_impact",
                0,
            )
        ),

        "response_time": safe_number(
            result.get(
                "response_time",
                0,
            )
        ),

        "response_length": response_length,

        "classification": str(
            classification
        ),

        "severity": str(
            severity
        ),

        "status": str(
            status
        ),

        "success": bool(
            result.get(
                "success",
                status == "Success",
            )
        ),

        "oracle_keywords": result.get(
            "oracle_keywords",
            [],
        ),
    }


def build_dashboard_summary(
    results: List[dict],
    providers: List[str],
) -> dict:
    """
    Builds all dashboard statistics.

    IMPORTANT:
    Before a campaign runs, the frontend uses zeros.

    After a campaign completes, these values are calculated
    exclusively from returned campaign results.
    """

    executed_results = [
        result
        for result in results
        if result.get("status")
        != "Infrastructure Error"
    ]

    failed_results = [
        result
        for result in results
        if result.get("status")
        == "Infrastructure Error"
    ]

    total_executed = len(
        executed_results
    )

    total_failed = len(
        failed_results
    )

    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    safe = sum(
        1
        for result in executed_results
        if result.get("severity") == "Safe"
    )

    warning = sum(
        1
        for result in executed_results
        if result.get("severity")
        in ["Warning", "High"]
    )

    critical = sum(
        1
        for result in executed_results
        if result.get("severity") == "Critical"
    )

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    risk_scores = [
        safe_number(
            result.get("score", 0)
        )
        for result in executed_results
    ]

    average_risk = (
        sum(risk_scores) / len(risk_scores)
        if risk_scores
        else 0
    )

    # --------------------------------------------------------
    # LVI
    # --------------------------------------------------------

    lvi_scores = [
        safe_number(
            result.get("lvi_score", 0)
        )
        for result in executed_results
    ]

    average_lvi = (
        sum(lvi_scores) / len(lvi_scores)
        if lvi_scores
        else 0
    )

    highest_lvi = (
        max(lvi_scores)
        if lvi_scores
        else 0
    )

    lowest_lvi = (
        min(lvi_scores)
        if lvi_scores
        else 0
    )

    critical_lvi = sum(
        1
        for value in lvi_scores
        if value >= 80
    )

    # --------------------------------------------------------
    # Attack distribution
    # --------------------------------------------------------

    attack_distribution = {}

    for result in executed_results:

        attack = result.get(
            "attack_category",
            "Unknown",
        )

        attack_distribution[attack] = (
            attack_distribution.get(
                attack,
                0,
            )
            + 1
        )

    # --------------------------------------------------------
    # Provider comparison
    # --------------------------------------------------------

    provider_comparison = []

    for provider in providers:

        provider_results = [
            result
            for result in executed_results
            if result.get("provider")
            == provider
        ]

        provider_risks = [
            safe_number(
                result.get(
                    "score",
                    0,
                )
            )
            for result in provider_results
        ]

        provider_lvi = [
            safe_number(
                result.get(
                    "lvi_score",
                    0,
                )
            )
            for result in provider_results
        ]

        provider_critical = sum(
            1
            for result in provider_results
            if result.get("severity")
            == "Critical"
        )

        provider_warning = sum(
            1
            for result in provider_results
            if result.get("severity")
            in ["Warning", "High"]
        )

        provider_safe = sum(
            1
            for result in provider_results
            if result.get("severity")
            == "Safe"
        )

        provider_count = len(
            provider_results
        )

        provider_comparison.append(
            {
                "provider": provider,

                "tests": provider_count,

                "average_risk": round(
                    (
                        sum(provider_risks)
                        / len(provider_risks)
                    )
                    if provider_risks
                    else 0,
                    2,
                ),

                "average_lvi": round(
                    (
                        sum(provider_lvi)
                        / len(provider_lvi)
                    )
                    if provider_lvi
                    else 0,
                    2,
                ),

                "critical": provider_critical,

                "warning": provider_warning,

                "safe": provider_safe,
            }
        )

    return {
        "estimated": 0,
        "executed": total_executed,
        "failed": total_failed,

        "average_risk": round(
            average_risk,
            2,
        ),

        "average_lvi": round(
            average_lvi,
            2,
        ),

        "highest_lvi": round(
            highest_lvi,
            2,
        ),

        "lowest_lvi": round(
            lowest_lvi,
            2,
        ),

        "critical_lvi": critical_lvi,

        "safe": safe,

        "warning": warning,

        "critical": critical,

        "attack_distribution":
            attack_distribution,

        "provider_comparison":
            provider_comparison,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health_check():

    return {
        "success": True,
        "service": "AutoFuzzLLM",
        "status": "online",
    }


# ============================================================
# RUN CAMPAIGN
# ============================================================

@app.post("/api/campaign/run")
def run_campaign(request: CampaignRequest):
    """
    Starts a complete fuzzing campaign.

    The existing FuzzCampaign engine is reused.

    Streamlit UI objects are NOT used here.
    """

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if not request.providers:

        raise HTTPException(
            status_code=400,
            detail="At least one LLM provider must be selected.",
        )

    if request.seed_source in [
        "Custom Prompt",
        "Hybrid Mode ⭐",
    ]:

        if not request.custom_prompt.strip():

            raise HTTPException(
                status_code=400,
                detail="Custom prompt is required.",
            )

    dataset_name = normalize_dataset_name(
        request.dataset_name
    )

    # --------------------------------------------------------
    # Dataset validation
    # --------------------------------------------------------

    if request.seed_source in [
        "Built-in Dataset",
        "Hybrid Mode ⭐",
    ]:

        if not dataset_name:

            raise HTTPException(
                status_code=400,
                detail="Dataset must be selected.",
            )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    all_results = []

    failed_providers = []

    planned_tests = 0

    # --------------------------------------------------------
    # Provider execution
    # --------------------------------------------------------

    for provider in request.providers:

        try:

            campaign = FuzzCampaign(
                provider=provider,
                mutation_engine=(
                    "AI Generated Mutations "
                    "(Recommended)"
                ),
            )

            model_results, completed_tests, model_planned_tests = (
                campaign.run(

                    seed_prompt=(
                        request.custom_prompt
                        if request.seed_source
                        in [
                            "Custom Prompt",
                            "Hybrid Mode ⭐",
                        ]
                        else ""
                    ),

                    max_tests=request.mutations,

                    generations=request.generations,

                    dataset_name=dataset_name,

                    initial_seed_count=(
                        request.initial_seed_count
                        if request.seed_source
                        != "Custom Prompt"
                        else 0
                    ),

                    seed_source=request.seed_source,

                    seed_pool_size=request.seed_pool_size,

                    fitness_threshold=request.fitness_threshold,

                    resume_data=None,

                    # ------------------------------------------------
                    # IMPORTANT
                    # These are None because Streamlit is no longer
                    # responsible for rendering progress.
                    # ------------------------------------------------

                    progress_bar=None,

                    status_text=None,

                    completed_tests=0,

                    total_tests=1,
                )
            )

            planned_tests += safe_int(
                model_planned_tests
            )

            if isinstance(
                model_results,
                list,
            ):

                all_results.extend(
                    model_results
                )

        except Exception as exc:

            failed_providers.append(
                {
                    "provider": provider,
                    "error": str(exc),
                }
            )

            print(
                f"[ERROR] Provider {provider}: "
                f"{exc}"
            )

            traceback.print_exc()

    # --------------------------------------------------------
    # Serialize results
    # --------------------------------------------------------

    serialized_results = [
        serialize_result(result)
        for result in all_results
    ]

    # --------------------------------------------------------
    # Build dashboard data
    # --------------------------------------------------------

    summary = build_dashboard_summary(
        serialized_results,
        request.providers,
    )

    # Real planned number returned by campaign.
    summary["estimated"] = planned_tests

    # --------------------------------------------------------
    # Final API response
    # --------------------------------------------------------

    return {
        "success": True,

        "message": (
            "Campaign completed."
            if not failed_providers
            else "Campaign completed with provider errors."
        ),

        "providers": request.providers,

        "failed_providers":
            failed_providers,

        "summary": summary,

        "results": serialized_results,
    }


# ============================================================
# LIVE CONVERSATION
# ============================================================

@app.post("/api/conversation")
def conversation(
    request: ConversationRequest
):
    """
    Executes the Live Conversation Fuzzer.
    """

    if not request.provider:

        raise HTTPException(
            status_code=400,
            detail="Provider is required.",
        )

    try:

        campaign = FuzzCampaign(
            provider=request.provider
        )

        messages = request.messages

        response = (
            campaign.executor
            .run_conversation(messages)
        )

        return {
            "success": True,
            "provider": request.provider,
            "response": response,
        }

    except Exception as exc:

        traceback.print_exc()

        return {
            "success": False,
            "provider": request.provider,
            "response": "",
            "error": str(exc),
        }


# ============================================================
# SERVE FRONTEND
# ============================================================
# ============================================================
# FRONTEND ROUTES
# ============================================================

@app.get("/")
async def serve_frontend():

    if not INDEX_FILE.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                f"Frontend index file not found: "
                f"{INDEX_FILE}"
            ),
        )

    return FileResponse(
        path=str(INDEX_FILE),
        media_type="text/html",
    )


# ============================================================
# FRONTEND STATIC FILES
# ============================================================
#
# Browser URLs:
#
# /frontend/components.css
# /frontend/app.js
#
# Physical files:
#
# frontend/components.css
# frontend/app.js
#
# ============================================================

app.mount(
    "/frontend",
    StaticFiles(
        directory=str(FRONTEND_DIR),
        html=False,
    ),
    name="frontend",
)