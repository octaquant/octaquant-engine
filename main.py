from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from octaquant.api.app import app


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
