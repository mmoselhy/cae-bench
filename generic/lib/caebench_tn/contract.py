"""The neutral output contract: `/tmp/agent/submission/result.json`.

```json
{
  "solver":  {"name": "openfoam", "version": "v2412"},
  "replay":  "replay.sh",
  "native_results": ["case/1000/U", "case/constant/polyMesh/points"],
  "kpis": {
    "<kpi>": {"value": 1.23,
              "source": {"kind": "file_extract",
                         "path": "/tmp/agent/submission/results.csv",
                         "extract": "awk -F, 'NR==2 {print $1}'"}}
  }
}
```

Validation here is structural only. What the score reads is decided by the
track evaluator (`core.py`), and the `kpis` claims are re-extracted for
attribution, never scored -- scoring them would change scores relative to the
original benchmark, whose evaluators derive every KPI themselves.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

RESULT_NAME = "result.json"
REPLAY_NAME = "replay.sh"


@dataclass
class Contract:
    ok: bool
    problems: list[str] = field(default_factory=list)
    solver_name: str | None = None
    solver_version: str | None = None
    replay: str = REPLAY_NAME
    native_results: list[str] = field(default_factory=list)
    kpis: dict[str, Any] = field(default_factory=dict)


def load(submission: Path) -> Contract:
    path = submission / RESULT_NAME
    if not path.is_file():
        return Contract(False, [f"{RESULT_NAME} missing from the submission root"])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return Contract(False, [f"{RESULT_NAME} is not valid JSON: {exc}"])
    if not isinstance(data, dict):
        return Contract(False, [f"{RESULT_NAME} must be a JSON object"])

    problems: list[str] = []
    solver = data.get("solver")
    name = version = None
    if isinstance(solver, dict):
        name = solver.get("name")
        version = solver.get("version")
    if not isinstance(name, str) or not name.strip():
        problems.append("solver.name missing")
        name = None
    if not isinstance(version, str) or not version.strip():
        problems.append("solver.version missing")
        version = None

    replay = data.get("replay", REPLAY_NAME)
    if replay != REPLAY_NAME:
        problems.append(f"replay must be {REPLAY_NAME!r} at the submission root, got {replay!r}")
    if not (submission / REPLAY_NAME).is_file():
        problems.append(f"{REPLAY_NAME} missing from the submission root")

    native = data.get("native_results", [])
    if not isinstance(native, list) or not all(isinstance(p, str) for p in native):
        problems.append("native_results must be a list of paths")
        native = []

    kpis = data.get("kpis", {})
    if not isinstance(kpis, dict):
        problems.append("kpis must be an object")
        kpis = {}

    return Contract(
        ok=not problems, problems=problems,
        solver_name=name.strip().lower() if name else None,
        solver_version=version, replay=REPLAY_NAME,
        native_results=list(native), kpis=kpis,
    )
