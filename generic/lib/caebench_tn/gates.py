"""Equivalence gates for the opensource profile.

    python3 -m caebench_tn.gates run --set original|generic [--case GLOB] [-n 2]
    python3 -m caebench_tn.gates collect --set original|generic
    python3 -m caebench_tn.gates diff                 # gate D
    python3 -m caebench_tn.gates negatives [--case GLOB] [-n 2]   # gate C (task-level)
    python3 -m caebench_tn.gates parity [--rel-tol 1e-9]          # gate B + PARITY.md (gate E)

Every number comes from a real `harbor run --agent oracle` (or a negative-
control "oracle"); nothing is inferred. Jobs live in generic/results/jobs
(gitignored); the per-KPI digests this writes into generic/results/*.json are
committed, because they are what PARITY.md is built from.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

from .generate import GENERIC, REPO

RESULTS = GENERIC / "results"
JOBS = RESULTS / "jobs"
HARBOR = shutil.which("harbor") or str(Path.home() / ".local/bin/harbor")


# ── task discovery ───────────────────────────────────────────────────────────

def original_tasks(pattern: str | None = None) -> list[Path]:
    out = sorted(p.parent for p in (REPO / "cases").rglob("task.toml")
                 if "_template" not in p.parts and "_phase2" not in p.parts)
    return [p for p in out if _match(p.relative_to(REPO / "cases"), pattern)]


def generic_tasks(profile: str = "opensource", pattern: str | None = None) -> list[Path]:
    root = GENERIC / "dist" / profile
    out = sorted(p.parent for p in root.rglob("task.toml")) if root.exists() else []
    return [p for p in out if _match(p.relative_to(root), pattern)]


def _match(rel: Path, pattern: str | None) -> bool:
    return not pattern or fnmatch.fnmatch(str(rel), pattern) or fnmatch.fnmatch(rel.name, pattern)


def _rel(task: Path) -> str:
    """`<domain>/<sub>/<case>`, the key both sets share."""
    parts = task.parts
    return "/".join(parts[-3:])


# ── running ──────────────────────────────────────────────────────────────────

def run_tasks(tasks: list[Path], set_name: str, n: int, agent: str = "oracle") -> None:
    JOBS.mkdir(parents=True, exist_ok=True)
    for task in tasks:
        key = _rel(task).replace("/", "__")
        job = f"{set_name}__{key}"
        if any((JOBS / job).glob("*/verifier/reward.json")):
            print(f"[skip] {job} (already scored)")
            continue
        if (JOBS / job).exists():
            shutil.rmtree(JOBS / job)
        print(f"[run ] {job}", flush=True)
        cmd = [HARBOR, "run", "-p", str(task), "--agent", agent, "-y", "-q",
               "-o", str(JOBS), "--job-name", job]
        subprocess.run(cmd, check=False)


def run_parallel(tasks: list[Path], set_name: str, n: int, agent: str = "oracle") -> None:
    """n worker processes, each draining its own slice."""
    if n <= 1:
        return run_tasks(tasks, set_name, 1, agent)
    procs = []
    for i in range(n):
        chunk = tasks[i::n]
        if not chunk:
            continue
        args = [sys.executable, "-m", "caebench_tn.gates", "_worker", "--set", set_name,
                "--agent", agent, *map(str, chunk)]
        procs.append(subprocess.Popen(args, cwd=str(GENERIC / "lib"),
                                      env={**os.environ, "PYTHONPATH": str(GENERIC / "lib")}))
    for p in procs:
        p.wait()


# ── collecting ───────────────────────────────────────────────────────────────

def kpis_from_detail(detail: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Per-KPI {value, score} from any of the reward_detail shapes in play."""
    if "track_detail" in detail:          # TN, trace track
        detail = detail["track_detail"]
    if "scoring_components" in detail:     # csv interface (upstream or TN)
        return {k: {"value": v.get("value"), "score": v.get("score")}
                for k, v in detail["scoring_components"].items()}
    per = detail.get("dimensions", {}).get("kpi_accuracy", {}).get("per_kpi") or {}
    return {k: {"value": v.get("value"), "score": v.get("score")} for k, v in per.items()}


def collect(set_name: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for job in sorted(JOBS.glob(f"{set_name}__*")):
        key = job.name[len(set_name) + 2:].replace("__", "/")
        trials = [t for t in job.iterdir() if t.is_dir()]
        if not trials:
            out[key] = {"status": "no_trial"}
            continue
        trial = trials[0]
        reward = trial / "verifier" / "reward.json"
        detail = trial / "verifier" / "reward_detail.json"
        entry: dict[str, Any] = {"trial": str(trial.relative_to(GENERIC))}
        if reward.is_file():
            entry["score"] = json.loads(reward.read_text())["score"]
        else:
            entry["score"] = None
            res = trial / "result.json"
            if res.is_file():
                r = json.loads(res.read_text())
                entry["exception"] = (r.get("exception_info") or {}).get("exception_type")
        if detail.is_file():
            d = json.loads(detail.read_text())
            entry["kpis"] = kpis_from_detail(d)
            for k in ("status", "failure_category", "verification", "error"):
                if k in d:
                    entry[k] = d[k] if k != "error" else str(d[k])[:300]
        out[key] = entry
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"{set_name}.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out


# ── gate D ───────────────────────────────────────────────────────────────────

BAND_FIELDS = ("gt_value", "pass_tol", "gross_error_tol", "physics_min", "physics_max",
               "T_good", "T_bad", "group", "gate")


def gate_d(profile: str = "opensource") -> dict[str, Any]:
    report: dict[str, Any] = {"checked": 0, "byte_identical": 0, "problems": []}
    for task in generic_tasks(profile):
        meta = tomllib.loads((task / "task.toml").read_text())["metadata"]["tn"]
        orig = REPO / meta["original_task"]
        for name in ("kpis.json", "spec.json"):
            a, b = (orig / "tests" / name).read_bytes(), (task / "tests" / name).read_bytes()
            report["checked"] += 1
            if a == b:
                report["byte_identical"] += 1
            else:
                report["problems"].append(f"{_rel(task)}/tests/{name} differs from {meta['original_task']}")
        ka = json.loads((orig / "tests" / "kpis.json").read_text())
        kb = json.loads((task / "tests" / "kpis.json").read_text())
        if ka.get("kpi_groups") != kb.get("kpi_groups"):
            report["problems"].append(f"{_rel(task)}: kpi_groups differ")
        for k, spec in ka["kpis"].items():
            for f in BAND_FIELDS:
                if spec.get(f) != kb["kpis"].get(k, {}).get(f):
                    report["problems"].append(f"{_rel(task)}: {k}.{f} differs")
    # And the upstream tree itself is untouched.
    diff = subprocess.run(["git", "status", "--porcelain", "--", "cases"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()
    report["cases_tree_clean"] = diff == ""
    if diff:
        report["problems"].append("cases/ has uncommitted changes:\n" + diff)
    report["passed"] = not report["problems"] and report["checked"] > 0
    return report


# ── gate C (task-level negative controls) ────────────────────────────────────

NEG_EMPTY = """#!/usr/bin/env bash
# Negative control: an empty submission.
mkdir -p /tmp/agent/submission
"""

NEG_PRINTF = r"""#!/usr/bin/env bash
# Negative control: a replay that prints the reference numbers without solving,
# with an otherwise valid contract.
set -euo pipefail
HERE="$(dirname "$(realpath "$0")")"
SUB=/tmp/agent/submission
mkdir -p "$SUB"
python3 "$HERE/neg_printf.py" "$SUB"
"""

NEG_PRINTF_PY = r'''import json, sys
from pathlib import Path
sub = Path(sys.argv[1]); cfg = json.loads((Path(__file__).parent / "neg.json").read_text())
cols = cfg["columns"]; vals = cfg["values"]
lines = ["printf '%s\\n' " + repr(",".join(cols)) + " > " + cfg["file"],
         "printf '%s\\n' " + repr(",".join(str(v) for v in vals)) + " >> " + cfg["file"]]
(sub / "replay.sh").write_text("#!/usr/bin/env bash\nset -e\ncd \"$(dirname \"$0\")\"\n" + "\n".join(lines) + "\n")
(sub / "replay.sh").chmod(0o755)
import subprocess; subprocess.run(["bash", "replay.sh"], cwd=sub, check=True)
(sub / "result.json").write_text(json.dumps({
    "solver": {"name": cfg["solver"], "version": "x"}, "replay": "replay.sh",
    "native_results": [], "kpis": {}}))
'''


def make_negative_tasks(pattern: str | None, profile: str = "opensource") -> list[Path]:
    """Copies of rendered tasks whose 'oracle' is a negative control."""
    root = RESULTS / "negative_tasks"
    made = []
    for task in generic_tasks(profile, pattern):
        spec = json.loads((task / "tests" / "spec.json").read_text())
        kpis = json.loads((task / "tests" / "kpis.json").read_text())["kpis"]
        tn = json.loads((task / "tests" / "tn.json").read_text())
        for kind in ("empty", "printf"):
            dst = root / kind / _rel(task)
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(task, dst)
            sol = dst / "solution"
            shutil.rmtree(sol)
            sol.mkdir()
            if kind == "empty":
                (sol / "solve.sh").write_text(NEG_EMPTY)
            else:
                if "interface" in spec:
                    cols = list(spec["interface"]["columns"])
                    file = spec["interface"]["file"]
                    by_col = {d.get("value"): kpis[k]["gt_value"] for k, d in spec["kpis"].items()}
                    vals = [by_col.get(c, 0.0) for c in cols]
                else:  # trace tracks: the KPI numbers alone, no trace
                    cols, file = list(kpis), "results.csv"
                    vals = [kpis[k]["gt_value"] for k in cols]
                (sol / "neg.json").write_text(json.dumps({"columns": cols, "values": vals, "file": file,
                                                          "solver": tn["solvers"][0]}))
                (sol / "neg_printf.py").write_text(NEG_PRINTF_PY)
                (sol / "solve.sh").write_text(NEG_PRINTF)
            (sol / "solve.sh").chmod(0o755)
            made.append(dst)
    return made


# ── gate B + E ───────────────────────────────────────────────────────────────

def parity(rel_tol: float, profile: str = "opensource") -> dict[str, Any]:
    base = json.loads((RESULTS / "original.json").read_text())
    gen = json.loads((RESULTS / "generic.json").read_text())
    neg = {k: (json.loads((RESULTS / f"neg_{k}.json").read_text()) if (RESULTS / f"neg_{k}.json").is_file() else {})
           for k in ("empty", "printf")}
    rows = []
    for key in sorted(set(base) | set(gen)):
        b, g = base.get(key, {}), gen.get(key, {})
        task = GENERIC / "dist" / profile / key
        label = reason = "-"
        if (task / "task.toml").is_file():
            meta = tomllib.loads((task / "task.toml").read_text())["metadata"]["tn"]
            label, reason = meta["portability"], meta["portability_reason"]
        kpi_ok, worst = True, 0.0
        bk, gk = b.get("kpis") or {}, g.get("kpis") or {}
        for k in set(bk) | set(gk):
            va, vb = (bk.get(k) or {}).get("value"), (gk.get(k) or {}).get("value")
            if va is None or vb is None:
                kpi_ok = kpi_ok and va is None and vb is None
                continue
            d = abs(float(va) - float(vb))
            worst = max(worst, d / max(1.0, abs(float(va))))
            if d > rel_tol * max(1.0, abs(float(va))):
                kpi_ok = False
        sb, sg = b.get("score"), g.get("score")
        same = sb is not None and sg is not None and sb == sg and kpi_ok and bool(gen.get(key))
        rows.append({"task": key, "baseline": sb, "generic": sg,
                     "neg_empty": neg["empty"].get(key, {}).get("score"),
                     "neg_printf": neg["printf"].get(key, {}).get("score"),
                     "diff": None if sb is None or sg is None else sg - sb,
                     "kpi_max_rel_diff": worst, "pass": same, "portability": label,
                     "portability_reason": reason})
    return {"rel_tol": rel_tol, "rows": rows}


def write_parity_md(rep: dict[str, Any]) -> Path:
    rows = rep["rows"]
    n_pass = sum(r["pass"] for r in rows)
    lines = [
        "# PARITY -- CAE-bench-TN `opensource` profile vs. original CAE-bench",
        "",
        "CAE-bench-TN is an unofficial, tool-neutral derivative of CAE-bench "
        "(svd-ai-lab/cae-bench, Apache-2.0). These are oracle runs, not agent scores.",
        "",
        "* **baseline** -- `harbor run --agent oracle` on the unmodified `cases/` task (gate A).",
        "* **generic** -- the same oracle, unchanged, wrapped to the neutral contract, on the "
        "task rendered with `generic/profiles/opensource.toml` (gate B).",
        f"* **pass** -- identical score and every KPI within `|a-b| <= {rep['rel_tol']:g} * max(1, |a|)`.",
        "",
        f"**{n_pass} / {len(rows)} tasks pass.** Generated by `python3 -m caebench_tn.gates parity`.",
        "",
        "Negative controls (gate C), run through Harbor on the rendered task: **empty** -- an empty "
        "submission; **printf** -- a valid contract whose `replay.sh` only prints the reference values.",
        "",
        "| task | baseline | generic | difference | max KPI rel. diff | pass | empty | printf | portability | reason |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    fmt = lambda v: "-" if v is None else f"{v:g}"  # noqa: E731
    for r in rows:
        lines.append(f"| `{r['task']}` | {fmt(r['baseline'])} | {fmt(r['generic'])} | {fmt(r['diff'])} | "
                     f"{r['kpi_max_rel_diff']:.2e} | {'yes' if r['pass'] else '**no**'} | "
                     f"{fmt(r['neg_empty'])} | {fmt(r['neg_printf'])} | "
                     f"{r['portability']} | {r['portability_reason']} |")
    path = GENERIC / "PARITY.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="caebench_tn.gates")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--set", choices=["original", "generic"], required=True)
    r.add_argument("--case"); r.add_argument("-n", type=int, default=2)
    w = sub.add_parser("_worker"); w.add_argument("--set", required=True); w.add_argument("--agent", default="oracle")
    w.add_argument("tasks", nargs="*")
    c = sub.add_parser("collect"); c.add_argument("--set", required=True)
    sub.add_parser("diff")
    ng = sub.add_parser("negatives"); ng.add_argument("--case"); ng.add_argument("-n", type=int, default=2)
    p = sub.add_parser("parity"); p.add_argument("--rel-tol", type=float, default=1e-9)
    a = ap.parse_args(argv)

    if a.cmd == "run":
        tasks = original_tasks(a.case) if a.set == "original" else generic_tasks("opensource", a.case)
        run_parallel(tasks, a.set, a.n)
        print(json.dumps(collect(a.set), indent=1)[:4000])
    elif a.cmd == "_worker":
        run_tasks([Path(t) for t in a.tasks], a.set, 1, a.agent)
    elif a.cmd == "collect":
        print(json.dumps(collect(a.set), indent=1))
    elif a.cmd == "diff":
        rep = gate_d()
        (RESULTS / "gate_d.json").parent.mkdir(parents=True, exist_ok=True)
        (RESULTS / "gate_d.json").write_text(json.dumps(rep, indent=2) + "\n")
        print(json.dumps(rep, indent=2))
        return 0 if rep["passed"] else 1
    elif a.cmd == "negatives":
        tasks = make_negative_tasks(a.case)
        for kind in ("empty", "printf"):
            run_parallel([t for t in tasks if f"/{kind}/" in str(t)], f"neg_{kind}", a.n)
            collect(f"neg_{kind}")
        for kind in ("empty", "printf"):
            res = json.loads((RESULTS / f"neg_{kind}.json").read_text())
            print(kind, {k: (v.get("score"), v.get("failure_category")) for k, v in res.items()})
    elif a.cmd == "parity":
        rep = parity(a.rel_tol)
        (RESULTS / "parity.json").write_text(json.dumps(rep, indent=2) + "\n")
        print(f"wrote {write_parity_md(rep).relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
