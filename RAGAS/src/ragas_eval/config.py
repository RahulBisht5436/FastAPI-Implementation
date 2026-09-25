import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_PLACEHOLDER_EVAL_SECRET = "change-me-to-a-long-random-secret"


def _load_chatbot_env(*, override: bool = False) -> None:
    candidates: list[Path] = []
    configured_root = os.getenv("CHATBOT_ROOT")
    if configured_root:
        candidates.append(Path(configured_root))
    candidates.extend(
        [
            Path.home() / "OneDrive" / "Desktop" / "personalChatBot",
            Path.home() / "Desktop" / "personalChatBot",
        ]
    )
    for root in candidates:
        env_file = root / ".env"
        if env_file.exists():
            load_dotenv(env_file, override=override)
            return


_load_chatbot_env()
load_dotenv(PROJECT_ROOT / ".env", override=True)

EVAL_SECRET = os.getenv("EVAL_SECRET", "")
if not EVAL_SECRET or EVAL_SECRET == _PLACEHOLDER_EVAL_SECRET:
    _load_chatbot_env(override=True)
    EVAL_SECRET = os.getenv("EVAL_SECRET", "")

EVAL_SECRET = EVAL_SECRET.strip()

CHATBOT_BASE_URL = os.getenv("CHATBOT_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
RAGAS_JUDGE_MODEL = os.getenv("RAGAS_JUDGE_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
EVAL_DATASET_PATH = os.getenv(
    "EVAL_DATASET_PATH",
    str(PROJECT_ROOT / "data" / "golden" / "v1.json"),
)
BASELINE_PATH = os.getenv(
    "BASELINE_PATH",
    str(PROJECT_ROOT / "baselines" / "baseline-v1.json"),
)
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", str(PROJECT_ROOT / "reports")))
EVAL_CONCURRENCY = max(1, int(os.getenv("EVAL_CONCURRENCY", "2")))
EVAL_TIMEOUT_SECONDS = float(os.getenv("EVAL_TIMEOUT_SECONDS", "120"))

DEFAULT_THRESHOLDS = {
    "faithfulness": 0.85,
    "answer_relevancy": 0.80,
    "context_precision": 0.75,
    "context_recall": 0.70,
}

REGRESSION_DROP_LIMIT = float(os.getenv("REGRESSION_DROP_LIMIT", "0.05"))
