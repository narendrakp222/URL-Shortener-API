"""
Vercel serverless entrypoint.

Vercel's Python runtime treats every file under ``api/`` as a serverless
function and looks for an ASGI callable named ``app`` in it. The FastAPI
application itself lives in ``app.main``; this module only re-exports it and
adds the workspace root to ``sys.path`` so ``app`` is importable even when the
function is loaded from a different working directory.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app  # noqa: E402  (must follow the sys.path setup)

__all__ = ["app"]
