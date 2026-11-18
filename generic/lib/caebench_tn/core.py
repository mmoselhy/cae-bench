"""The shared verifier core of CAE-bench-TN.

    contract check -> adapter selection -> track evaluation -> claim audit

* **Contract check** (`contract.py`): result.json, solver name/version,
  replay.sh. A submission without a valid contract scores 0.
* **Adapter selection**: the solver named in result.json must be offered by the
  task's profile for its domain, registered, `tested`, and able to serve the
  task's track. Anything else is reported as **unverified** and scores 0 --
  never as a pass.
* **Track evaluation** (the score):
    - `csv_interface` (cfd, packaging): clean copy -> adapter.strip ->
      `bash ./replay.sh` under the case's own budget -> adapter.solver_evidence
      -> `read_interface` + `score_kpis` from `tests/spec.json`. This is
      `openfoam_interface.main_from_case` / `calculix_interface.main_from_case`
      with the solver-specific calls moved behind the adapter.
    - `cantera_trace` / `pybamm_trace`: the upstream track evaluators run
      unchanged (`driver="replay.sh"`); their physics gates are solver-
      independent and stay. The adapter reads its evidence out of their detail.
  Scoring is upstream's: `score.band_score` / `pass_tol` / `_physics_pass`,
  reached through `csv_interface.score_kpis` and the trace evaluators.
* **Claim audit** (diagnostic only): every `kpis` claim in result.json is
  re-extracted with upstream's sandboxed `provenance.verify_source` and
  compared with the evaluator's own value. It never changes the score.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from sim_benchmark_verifier.csv_interface import read_interface, score_kpis
from sim_benchmark_verifier.provenance import verify_source

from . import VARIANT_NOTICE, adapters
from .adapters import InvalidSubmission
from .contract import REPLAY_NAME, Contract, load

SCHEMA = "caebench-tn-reward-v1"
SUBMISSION_ROOT = "/tmp/agent/submission"
DEFAULT_BUDGET_S = {"openfoam": 1800, "calculix": 2400}


class Failure(RuntimeError):
    def __init__(self, category: str, message: str):
        super().__init__(message)
        self.category = category


def _write(reward_dir: Path, score: float, detail: dict[str, Any]) -> None:
    reward_dir.mkdir(parents=True, exist_ok=True)
    detail["final_score"] = round(float(score), 6)
    (reward_dir / "reward.json").write_text(json.dumps({"score": round(float(score), 6)}, indent=2),
                                            encoding="utf-8")
    (reward_dir / "reward_detail.json").write_text(json.dumps(detail, indent=2, default=str),
                                                   encoding="utf-8")


def select_adapter(contract: Contract, tn: dict[str, Any]) -> tuple[Any, str]:
    """(adapter, "") when usable, else (None, why-unverified)."""
    name = contract.solver_name
    allowed = [s.lower() for s in tn.get("solvers", [])]
    if name is None:
        return None, "result.json names no solver"
    if name not in allowed:
        return None, f"solver {name!r} is not offered by profile {tn.get('profile')!r} for this task ({allowed})"
    adapter = adapters.get(name)
    if adapter is None:
        return None, f"no adapter is registered for solver {name!r}"
    if not adapter.tested:
        return None, f"the {name!r} adapter is an untested stub"
    if tn["track"] not in adapter.tracks:
        return None, f"the {name!r} adapter does not serve track {tn['track']!r}"
    return adapter, ""


# ── tracks ───────────────────────────────────────────────────────────────────

def csv_track(adapter, tests_dir: Path, submission: Path, reward_dir: Path,
              detail: dict[str, Any]) -> float:
    spec = json.loads((tests_dir / "spec.json").read_text(encoding="utf-8"))
    kpis = json.loads((tests_dir / "kpis.json").read_text(encoding="utf-8"))["kpis"]
    interface = spec["interface"]
    budget = int(spec.get("reproduction_timeout_s", DEFAULT_BUDGET_S.get(adapter.name, 1800)))
    detail["interface"] = interface
    detail["stage"] = "submission_validation"

    replay = submission / REPLAY_NAME
    if not replay.is_file() or replay.stat().st_size == 0:
        raise Failure("invalid_submission", f"missing reproducible case inputs: {REPLAY_NAME}")
    try:
        adapter.validate_inputs(submission)
    except InvalidSubmission as exc:
        raise Failure("invalid_submission", str(exc)) from exc

    with tempfile.TemporaryDirectory(prefix=f"{spec['case_id']}-tn-") as temp:
        work = Path(temp) / "case"
        shutil.copytree(submission, work)
        detail["removed_prior_artifacts"] = adapter.strip(
            work, (interface["file"],), tuple(spec.get("preserve") or ()))

        detail["stage"] = "reproduction"
        try:
            run = adapter.run(work, f"bash ./{REPLAY_NAME}", timeout_s=budget,
                              log_path=reward_dir / "evaluator_replay.log")
        except Exception as exc:  # noqa: BLE001 -- categorised exactly as upstream
            category = "reproduction_timeout" if "timed out after" in str(exc) else "reproduction_failed"
            raise Failure(category, str(exc)) from exc
        detail["reproduction"] = {**run, "timeout_s": budget}

        detail["stage"] = "solver_evidence"
        evidence = adapter.solver_evidence(work)
        detail["solver_evidence"] = {"verdict": evidence.verdict, "why": evidence.why, **evidence.detail}
        if evidence.verdict == "unverified":
            raise Failure("unverified_solver", evidence.why)
        if evidence.verdict != "pass":
            raise Failure("invalid_physics_setup",
                          f"{evidence.why}; {interface['file']} was not produced by solving")

        detail["stage"] = "extraction"
        cols = read_interface(work / interface["file"], list(interface["columns"]),
                              int(interface.get("min_rows", 1)), list(interface.get("labels") or ()))
        detail["interface_rows"] = len(next(iter(cols.values())))

        detail["stage"] = "scoring"
        score, per_kpi = score_kpis(cols, spec["kpis"], kpis)
        detail["scoring_components"] = per_kpi
        detail["evaluator_values"] = {k: v["value"] for k, v in per_kpi.items()}
        detail["stage"] = "complete"
        return score


def trace_track(adapter, tests_dir: Path, submission: Path, reward_dir: Path,
                detail: dict[str, Any]) -> float:
    if adapter.name == "cantera":
        from sim_benchmark_verifier import native_cantera as native
    else:
        from sim_benchmark_verifier import native_pybamm as native

    track_dir = reward_dir / "track"
    prev = {k: os.environ.get(k) for k in ("SIM_BENCH_SUBMISSION", "SIM_BENCH_REWARD_DIR")}
    os.environ["SIM_BENCH_SUBMISSION"] = str(submission)
    os.environ["SIM_BENCH_REWARD_DIR"] = str(track_dir)
    try:
        native.main_from_case(tests_dir, driver=REPLAY_NAME)
    finally:
        for k, v in prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    native_detail = json.loads((track_dir / "reward_detail.json").read_text(encoding="utf-8"))
    detail["track_detail"] = native_detail
    evidence = adapter.evidence_from_detail(native_detail)
    detail["solver_evidence"] = {"verdict": evidence.verdict, "why": evidence.why, **evidence.detail}
    per_kpi = (native_detail.get("dimensions", {}).get("kpi_accuracy", {}).get("per_kpi") or {})
    detail["evaluator_values"] = {k: v.get("value") for k, v in per_kpi.items()}
    # The evidence dimensions are a subset of upstream's GATES, so this product
    # can only agree with `final_score`; it is applied so the adapter, not the
    # track, is what a reader sees deciding "a real solve happened".
    return float(native_detail["final_score"]) * (1.0 if evidence.verdict == "pass" else 0.0)


TRACKS = {"csv_interface": csv_track, "cantera_trace": trace_track, "pybamm_trace": trace_track}


# ── claim audit (diagnostic) ────────────────────────────────────────────────

def audit_claims(contract: Contract, submission: Path, kpi_names: list[str],
                 evaluator_values: dict[str, Any], pass_tols: dict[str, float]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name in kpi_names:
        claim = contract.kpis.get(name)
        if claim is None:
            out[name] = {"provenance_stage": "P0_hallucination", "why": "no claim in result.json"}
            continue
        if isinstance(claim, dict) and isinstance(claim.get("source"), dict):
            src = dict(claim["source"])
            path = src.get("path")
            # Re-root claims written against the canonical mount when the
            # verifier runs on a copy elsewhere (local tests).
            if isinstance(path, str) and path.startswith(SUBMISSION_ROOT) and str(submission) != SUBMISSION_ROOT:
                src["path"] = str(submission) + path[len(SUBMISSION_ROOT):]
            claim = {**claim, "source": src}
        res = verify_source(claim, [])
        entry: dict[str, Any] = {"provenance_stage": "P4_pass" if res.ok else "P3_or_lower",
                                 "why": res.why, "extracted": res.extracted}
        ev = evaluator_values.get(name)
        try:
            claimed = float(claim["value"])  # type: ignore[index]
        except (TypeError, ValueError, KeyError):
            claimed = None
        if ev is not None and claimed is not None:
            entry["evaluator_value"] = ev
            entry["claimed_value"] = claimed
            entry["claim_minus_evaluator"] = claimed - float(ev)
            tol = pass_tols.get(name)
            if tol is not None:
                entry["claim_within_pass_tol_of_evaluator"] = abs(claimed - float(ev)) <= tol
        out[name] = entry
    return out


# ── entry point ──────────────────────────────────────────────────────────────

def verify(tests_dir: Path, submission: Path, reward_dir: Path) -> dict[str, Any]:
    tn = json.loads((tests_dir / "tn.json").read_text(encoding="utf-8"))
    kpis_doc = json.loads((tests_dir / "kpis.json").read_text(encoding="utf-8"))
    contract = load(submission)
    detail: dict[str, Any] = {
        "schema_version": SCHEMA,
        "variant": VARIANT_NOTICE,
        "case_id": tn["case_id"],
        "profile": tn["profile"],
        "track": tn["track"],
        "contract": {"ok": contract.ok, "problems": contract.problems,
                     "solver": contract.solver_name, "solver_version": contract.solver_version,
                     "native_results": contract.native_results},
        "status": "running",
    }
    score = 0.0
    try:
        if not contract.ok:
            raise Failure("contract_invalid", "; ".join(contract.problems))
        adapter, why = select_adapter(contract, tn)
        if adapter is None:
            detail["verification"] = "unverified"
            raise Failure("unverified_solver", why)
        detail["adapter"] = adapter.name
        score = TRACKS[tn["track"]](adapter, tests_dir, submission, reward_dir, detail)
        detail["verification"] = "verified"
        detail["status"] = "completed"
    except Failure as exc:
        score = 0.0
        detail["status"] = "failed"
        detail["failure_category"] = exc.category
        detail["error"] = str(exc)
        detail.setdefault("verification", "unverified" if exc.category == "unverified_solver" else "failed")
    except Exception as exc:  # noqa: BLE001 -- an evaluator bug stays distinguishable
        score = 0.0
        detail["status"] = "failed"
        detail["failure_category"] = "evaluator_error"
        detail["error"] = f"{type(exc).__name__}: {exc}"

    try:
        kp = kpis_doc["kpis"]
        detail["claim_audit"] = audit_claims(
            contract, submission, list(kp), detail.get("evaluator_values", {}),
            {k: float(v.get("pass_tol", v.get("T_good", 0)) or 0) for k, v in kp.items()})
    except Exception as exc:  # noqa: BLE001 -- diagnostic only
        detail["claim_audit_error"] = f"{type(exc).__name__}: {exc}"

    _write(reward_dir, score, detail)
    return detail


def main(argv: list[str] | None = None) -> int:
    import sys
    args = list(sys.argv[1:] if argv is None else argv)
    tests_dir = Path(args[0]) if args else Path("/tests")
    submission = Path(os.environ.get("SIM_BENCH_SUBMISSION", SUBMISSION_ROOT))
    reward_dir = Path(os.environ.get("SIM_BENCH_REWARD_DIR", "/logs/verifier"))
    detail = verify(tests_dir.resolve(), submission, reward_dir)
    print(json.dumps({"score": detail["final_score"], "status": detail["status"],
                      "verification": detail.get("verification"),
                      "failure_category": detail.get("failure_category")}, indent=2))
    return 0
