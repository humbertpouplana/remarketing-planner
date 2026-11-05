from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def load_params(path=DATA / "params.json") -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
