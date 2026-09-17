"""
Vercel build hook (`vercel.json` -> "buildCommand").

Installs the slim runtime dependency set used by the serverless function. The
builder installs dependencies from requirements.txt by default, which would also
pull the test-only packages into the function bundle.
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REQUIREMENTS = PROJECT_ROOT / "requirements-vercel.txt"

if not REQUIREMENTS.is_file():
    sys.exit(f"Missing dependency manifest: {REQUIREMENTS}")

result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "--no-cache-dir", "-r", str(REQUIREMENTS)],
    cwd=PROJECT_ROOT,
)
sys.exit(result.returncode)
