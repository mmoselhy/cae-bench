"""Record a human reference solution's KPIs against the existing bands.

    python3 -m caebench_tn.calibrate --profile P --task generic/dist/P/<domain>/<sub>/<case> \
        --submission DIR [--image IMAGE] [--note "who/what/when"]

Runs the CAE-bench-TN verifier on DIR (a complete submission: replay.sh,
result.json, inputs) inside the task's verifier image -- or on this host with
--local -- and writes `generic/calibration/<P>/<case>.json` with, per KPI, the
reference solution's value, `gt_value`, `pass_tol`, the signed error and
whether it falls inside the band.

It NEVER writes to kpis.json and never proposes a new band or reference
value: a reference solution landing outside a band is a finding for a human
to adjudicate, recorded as such.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .generate import GENERIC


def _verifier_image(task: Path) -> str:
    m = re.search(r"(?m)^FROM\s+(\S+)", (task / "tests" / "Dockerfile").read_text())
    if not m:
        raise SystemExit("tests/Dockerfile has no FROM line")
    return m.group(1)


def run_verifier(task: Path, submission: Path, image: str | None, local: bool) -> dict:
    out = Path(tempfile.mkdtemp(prefix="tn-calib-"))
    if local:
        from .core import verify
        return verify(task / "tests", submission.resolve(), out)
    image = image or _verifier_image(task)
    cmd = ["docker", "run", "--rm", "--network", "none", "--user", "0",
           "-v", f"{(task / 'tests').resolve()}:/tests:ro",
           "-v", f"{submission.resolve()}:/tmp/agent/submission:ro",
           "-v", f"{out}:/logs/verifier", image, "bash", "/tests/test.sh"]
    subprocess.run(cmd, check=False)
    detail = json.loads((out / "reward_detail.json").read_text())
    shutil.rmtree(out, ignore_errors=True)
    return detail


def summarise(task: Path, detail: dict) -> dict:
    from .gates import kpis_from_detail
    kpis = json.loads((task / "tests" / "kpis.json").read_text())["kpis"]
    got = kpis_from_detail(detail)
    rows = {}
    for name, spec in kpis.items():
        v = (got.get(name) or {}).get("value")
        tol = float(spec.get("pass_tol", spec.get("T_good")))
        row = {"gt_value": spec["gt_value"], "pass_tol": tol, "value": v}
        if v is not None:
            err = float(v) - float(spec["gt_value"])
            row.update({"error": err, "error_in_band_widths": abs(err) / tol if tol else None,
                        "inside_band": abs(err) <= tol,
                        "inside_physics_window": float(spec["physics_min"]) <= float(v) <= float(spec["physics_max"])})
        rows[name] = row
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="caebench_tn.calibrate")
    ap.add_argument("--profile", required=True)
    ap.add_argument("--task", type=Path, required=True)
    ap.add_argument("--submission", type=Path, required=True)
    ap.add_argument("--image")
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--note", default="")
    a = ap.parse_args(argv)

    detail = run_verifier(a.task, a.submission, a.image, a.local)
    record = {
        "profile": a.profile,
        "task": str(a.task),
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "note": a.note,
        "solver": detail.get("contract", {}).get("solver"),
        "solver_version": detail.get("contract", {}).get("solver_version"),
        "verifier_status": detail.get("status"),
        "verification": detail.get("verification"),
        "failure_category": detail.get("failure_category"),
        "score": detail.get("final_score"),
        "kpis": summarise(a.task, detail),
        "policy": "Recorded only. Bands and reference values are never changed by this tool.",
    }
    dst = GENERIC / "calibration" / a.profile / f"{a.task.name}.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(record, indent=2) + "\n")
    inside = all(r.get("inside_band") for r in record["kpis"].values())
    print(json.dumps({"written": str(dst), "all_inside_band": inside,
                      "kpis": record["kpis"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
