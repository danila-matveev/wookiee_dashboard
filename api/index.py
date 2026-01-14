import os
import sys
import json
import time
import logging

# Configure logging to stdout (Vercel collects stdout as logs)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

logger.info(f"api/index.py: Starting import, ROOT={ROOT}, sys.path={sys.path[:3]}...")

try:
    from apps.telegram_assistant.main import app  # noqa: E402
    logger.info("api/index.py: Successfully imported app from apps.telegram_assistant.main")
except Exception as e:
    logger.error(f"api/index.py: Failed to import app: {e}", exc_info=True)
    raise

# Vercel Python builder automatically detects ASGI app via variable name "app"
logger.info("api/index.py: ASGI app 'app' exported for Vercel")

# region agent log
def _agent_log(hypothesis_id: str, location: str, message: str, data: dict | None = None) -> None:
    """
    Debug-mode NDJSON logger.
    IMPORTANT: do not log secrets (tokens, keys, full env).
    """
    try:
        payload = {
            "sessionId": "debug-session",
            "runId": os.getenv("AGENT_RUN_ID", "pre-fix"),
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000),
        }
        log_path = os.path.join(ROOT, ".cursor", "debug.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # Never break app because of debug logging.
        pass


_agent_log(
    "H_build_runtime",
    "api/index.py:init",
    "api module imported; ASGI app exported",
    {
        "rootInSyspath": ROOT in sys.path,
        "pythonVersion": sys.version.split(" ")[0],
        "hasVercelEnv": bool(os.getenv("VERCEL")),
    },
)
# endregion agent log
