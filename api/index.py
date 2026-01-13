import os
import sys
import json
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from apps.telegram_assistant.main import app  # noqa: E402

# Vercel Python builder automatically detects ASGI app via variable name "app"
# Nothing else required here.

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
