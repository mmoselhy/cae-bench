#!/usr/bin/env python3
"""Adapt an upstream CAE-bench oracle's finished run to the CAE-bench-TN contract.

Runs in the agent container after the UNCHANGED upstream `solve.sh`. Writes:

* `replay.sh` -- execs the upstream oracle's own entry point (`Allrun`,
  `run_case.sh` or `run_case.py`), so the evaluator's replay is the upstream
  oracle's run and nothing else;
* `tn_kpis.csv` -- each KPI computed by the upstream derivation from the run's
  own `results.csv` (deterministic post-processing of that run);
* `result.json` -- solver name/version, replay, native result files, and one
  `file_extract` claim per KPI pointing at `tn_kpis.csv`.

Self-contained on purpose: it ships in solution/ next to `tn_oracle.json`
and imports only what the agent image already has.
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUBMISSION = Path(os.environ.get("SIM_BENCH_SUBMISSION", "/tmp/agent/submission"))

NATIVE_GLOBS = {
    "openfoam": ["**/constant/polyMesh/points", "**/[1-9]*/U", "**/[0-9]*.[0-9]*/U", "**/log.*"],
    "calculix": ["**/*.frd", "**/*.dat", "**/*.sta"],
    "cantera": ["results*.csv", "*.csv"],
    "pybamm": ["results*.csv"],
}


def solver_version(solver: str) -> str:
    try:
        if solver == "openfoam":
            v = os.environ.get("WM_PROJECT_VERSION")
            if v:
                return v
            out = subprocess.run(["bash", "-lc", "ls -d /usr/lib/openfoam/openfoam* 2>/dev/null | head -1"],
                                 capture_output=True, text=True).stdout.strip()
            return ("v" + out.rsplit("openfoam", 1)[-1]) if out else "unknown"
        if solver == "calculix":
            out = subprocess.run(["bash", "-c", "ccx -v 2>&1 | head -5"], capture_output=True, text=True).stdout
            for tok in out.replace(",", " ").split():
                if tok[:1].isdigit() and "." in tok:
                    return tok
            return "unknown"
        if solver == "cantera":
            import cantera
            return cantera.__version__
        if solver == "pybamm":
            import pybamm
            return pybamm.__version__
    except Exception:  # noqa: BLE001
        pass
    return "unknown"


def kpi_values(cfg: dict) -> dict[str, float]:
    spec = cfg["spec"]
    track = cfg["track"]
    if track == "csv_interface":
        from sim_benchmark_verifier.csv_interface import derive, read_interface
        itf = spec["interface"]
        cols = read_interface(SUBMISSION / itf["file"], list(itf["columns"]),
                              int(itf.get("min_rows", 1)), list(itf.get("labels") or ()))
        return {k: float(derive(cols, d)) for k, d in spec["kpis"].items()}
    if track == "cantera_trace":
        from sim_benchmark_verifier import native_cantera as nc
        s = nc.CanteraSpec(**{k: v for k, v in spec.items() if k not in nc._RETIRED_SPEC_KEYS})
        cols = nc.read_results_csv(SUBMISSION / nc.RESULTS_NAME)
        aux = nc.read_results_csv(SUBMISSION / s.second_profile) if s.second_profile else None
        out = nc.with_declared(nc.EXTRACTORS[s.kind], s)(cols, s, aux)
    else:
        from sim_benchmark_verifier import native_pybamm as npb
        s = npb.PyBaMMSpec(**spec)
        cols = npb.read_results_csv(SUBMISSION / npb.RESULTS_NAME)
        out = npb.EXTRACTORS[s.kind](cols, s)
    return {k: float(out[k]) for k in cfg["kpi_names"] if k in out}


def main() -> int:
    cfg = json.loads((HERE / "tn_oracle.json").read_text(encoding="utf-8"))
    SUBMISSION.mkdir(parents=True, exist_ok=True)

    replay = SUBMISSION / "replay.sh"
    replay.write_text(
        "#!/usr/bin/env bash\n"
        "# Replays the upstream CAE-bench oracle's own entry point, unchanged.\n"
        "set -euo pipefail\n"
        'cd "$(dirname "$(realpath "$0")")"\n'
        f"exec {cfg['entry']}\n", encoding="utf-8")
    replay.chmod(0o755)

    try:
        values = kpi_values(cfg)
    except Exception as exc:  # noqa: BLE001 -- claims are diagnostic; never block the oracle
        print(f"[tn-oracle] KPI claim derivation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        values = {}
    claims_file = SUBMISSION / "tn_kpis.csv"
    claims_file.write_text("kpi,value\n" + "".join(f"{k},{v!r}\n" for k, v in values.items()),
                           encoding="utf-8")

    native: list[str] = []
    for pattern in NATIVE_GLOBS.get(cfg["solver"], []):
        native += [str(Path(p).relative_to(SUBMISSION))
                   for p in glob.glob(str(SUBMISSION / pattern), recursive=True)]
    result = {
        "solver": {"name": cfg["solver"], "version": solver_version(cfg["solver"])},
        "replay": "replay.sh",
        "native_results": sorted(set(native))[:200],
        "kpis": {
            k: {"value": v, "source": {
                "kind": "file_extract",
                "path": str(claims_file),
                "extract": f"awk -F, '$1==\"{k}\" {{print $2}}'"}}
            for k, v in values.items()
        },
    }
    (SUBMISSION / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"[tn-oracle] result.json: solver={result['solver']}, kpis={list(values)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
