"""Render one Harbor dataset per profile from the neutral sources.

    python3 -m caebench_tn.generate --profile opensource [--case <glob>] [--force]

Inputs
  generic/cases/<domain>/<sub>/<case>/case.toml   neutral metadata
  generic/cases/<...>/prompt.md                   neutral prompt
  generic/cases/<...>/env/<profile>.md            optional task-specific profile facts
  generic/cases/<...>/inputs/                     optional neutral inputs (shipped beside the natives)
  generic/profiles/<profile>.toml                 what a profile provides + appendices
  cases/<original>/                               the upstream task (never modified)

Output
  generic/dist/<profile>/<domain>/<sub>/<case>/   a Harbor task
  generic/coverage/<profile>.md                   which tasks the profile covers

`tests/kpis.json` and `tests/spec.json` are copied byte-for-byte from the
upstream case: reference values and bands cannot drift here by construction,
and `caebench_tn.gates diff` (gate D) re-checks it on the rendered output.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import sys
import tomllib
from pathlib import Path

from . import VARIANT_NAMESPACE, VARIANT_NOTICE

REPO = Path(__file__).resolve().parents[3]
GENERIC = REPO / "generic"
LIB = GENERIC / "lib"
UPSTREAM_LIB = REPO / "lib" / "sim_benchmark_verifier" / "sim_benchmark_verifier"

# The upstream oracle's entry point, by domain -- what the rendered oracle's
# replay.sh execs, so the replay is literally the upstream oracle's own run.
ORIGINAL_ENTRY = {
    "cfd": "bash ./Allrun",
    "packaging": "bash ./run_case.sh",
    "combustion": "python3 run_case.py",
    "battery": "python3 run_case.py",
}

CONTRACT = """
## Deliverables (tool-neutral contract)

Work inside `/tmp/agent/submission/` -- that directory is what gets collected, so
build there rather than assembling it at the end. Required:

1. **`replay.sh`** at the submission root -- a non-interactive script that, run as
   `bash ./replay.sh` from a clean copy of the submission, re-solves the problem
   and rewrites the output file(s) described above. It must return non-zero on
   failure and finish within the time budget. The evaluator deletes every
   generated artifact -- solver output, logs, and the output file(s) themselves --
   before re-running it, so the result has to come from solving again. You may
   leave meshes, solver results and logs behind; nothing you leave can affect the
   score.
   Files the task supplies under `/tmp/agent/inputs/` are present at that same
   path when `replay.sh` is re-run; read them from there.
2. **The output file(s)** described above, written by `replay.sh`.{figure}
3. **`result.json`** at the submission root:

   ```json
   {{
     "solver": {{"name": "<solver>", "version": "<version>"}},
     "replay": "replay.sh",
     "native_results": ["<path of each solver result file, relative to the submission>"],
     "kpis": {{
       "<kpi>": {{"value": 0.0,
                 "source": {{"kind": "file_extract",
                            "path": "/tmp/agent/submission/<file>",
                            "extract": "<awk/sed/grep/cut/head/tail pipeline that prints the value>"}}}}
     }}
   }}
   ```

   `kpis` has one entry per reported quantity ({kpi_names}). The score is computed
   by the evaluator from the output file(s) it regenerates with `replay.sh`; the
   `kpis` claims are re-extracted and recorded for attribution. A `result.json`
   that is missing, or names a solver the evaluation environment cannot verify,
   scores zero.

Do not hand-write, edit or fabricate solver logs, result files or output files.
"""

FIGURE = """
   Also write **a figure** -- an image file (`.png` is fine) plotting your result,
   of the kind you would put in a report. It must be produced by `replay.sh`."""

TEST_SH = """#!/usr/bin/env bash
# CAE-bench-TN verifier entry point (unofficial tool-neutral variant).
set -euo pipefail
HERE="$(dirname "$(realpath "$0")")"
export PYTHONPATH="$HERE/_tn${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m caebench_tn.verify "$HERE"
"""

SOLVE_SH = """#!/usr/bin/env bash
# CAE-bench-TN oracle: the UNCHANGED upstream oracle, then the neutral contract.
set -euo pipefail
HERE="$(dirname "$(realpath "$0")")"
bash "$HERE/solve_original.sh"
python3 "$HERE/tn_oracle_finish.py"
"""


def load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def neutral_cases(pattern: str | None = None) -> list[Path]:
    out = sorted(p.parent for p in (GENERIC / "cases").rglob("case.toml"))
    if pattern:
        out = [p for p in out if fnmatch.fnmatch(str(p.relative_to(GENERIC / "cases")), pattern)
               or fnmatch.fnmatch(p.name, pattern)]
    return out


def coverage(profile: dict, case: dict) -> tuple[bool, list[str]]:
    if case["domain"] not in profile.get("domains", {}):
        return False, [f"domain:{case['domain']}"]
    missing = sorted(set(case["requires"]) - set(profile.get("provides", [])))
    return not missing, missing


def render_instruction(src: Path, case: dict, profile: dict, kpi_names: list[str]) -> str:
    prompt = (src / "prompt.md").read_text(encoding="utf-8").rstrip() + "\n"
    contract = CONTRACT.format(
        figure=FIGURE if case.get("figure") else "",
        kpi_names=", ".join(f"`{k}`" for k in kpi_names),
    )
    appendix = profile["domains"][case["domain"]]["appendix"].strip() + "\n"
    extra = src / "env" / f"{profile['name']}.md"
    if extra.is_file() and extra.read_text(encoding="utf-8").strip():
        appendix += extra.read_text(encoding="utf-8").rstrip() + "\n"
    return f"{prompt}{contract}\n{appendix}"


def render_task_toml(original: Path, case: dict, profile: dict, slug: str) -> str:
    text = original.read_text(encoding="utf-8")
    text, n = re.subn(r'(?m)^(name\s*=\s*)"[^"/]+/([^"]+)"',
                      lambda m: f'{m.group(1)}"{VARIANT_NAMESPACE}/{m.group(2)}"', text, count=1)
    if n != 1:
        raise SystemExit(f"{original}: could not rename [task].name")
    text = re.sub(r'(?m)^(description\s*=\s*")', r'\1[CAE-bench-TN, unofficial tool-neutral variant] ',
                  text, count=1)
    if not profile.get("inherit_images", False):
        dom = profile["domains"][case["domain"]]
        text = re.sub(r'(?m)^(docker_image\s*=\s*)"[^"]*"', lambda m: f'{m.group(1)}"{dom["docker_image"]}"', text)
    meta = {
        "variant": "CAE-bench-TN (unofficial)",
        "profile": profile["name"],
        "original_task": case["original"],
        "track": case["track"],
        "requires": case["requires"],
        "portability": case["portability"],
        "portability_reason": case["portability_reason"],
    }
    lines = ["", "# CAE-bench-TN: unofficial tool-neutral variant. Not a CAE-bench score.", "[metadata.tn]"]
    for k, v in meta.items():
        lines.append(f"{k} = {json.dumps(v)}")
    return text.rstrip() + "\n" + "\n".join(lines) + "\n"


def vendor(dst: Path) -> None:
    """Ship the verifier inside tests/, so it never depends on what the image baked in."""
    tn = dst / "_tn"
    if tn.exists():
        shutil.rmtree(tn)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "tests")
    shutil.copytree(LIB / "caebench_tn", tn / "caebench_tn", ignore=ignore)
    shutil.copytree(UPSTREAM_LIB, tn / "sim_benchmark_verifier", ignore=ignore)


def render_case(src: Path, profile: dict, out_root: Path) -> Path:
    case = load_toml(src / "case.toml")
    original = REPO / case["original"]
    rel = Path(case["original"]).relative_to("cases")
    dst = out_root / rel
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    slug_match = re.search(r'(?m)^name\s*=\s*"[^"/]+/([^"]+)"', (original / "task.toml").read_text())
    slug = slug_match.group(1) if slug_match else rel.name

    spec = json.loads((original / "tests" / "spec.json").read_text(encoding="utf-8"))
    kpis_doc = json.loads((original / "tests" / "kpis.json").read_text(encoding="utf-8"))
    # The KPIs the evaluator actually scores: csv tracks score only what
    # spec.json derives (kpis.json may carry retired entries); trace tracks
    # score every kpis.json entry.
    kpi_names = list(spec["kpis"]) if "interface" in spec else list(kpis_doc["kpis"])

    (dst / "task.toml").write_text(render_task_toml(original / "task.toml", case, profile, slug), encoding="utf-8")
    (dst / "instruction.md").write_text(render_instruction(src, case, profile, kpi_names), encoding="utf-8")

    # environment/: upstream fixtures unchanged, plus neutral inputs beside them.
    shutil.copytree(original / "environment", dst / "environment")
    if (src / "inputs").is_dir():
        shutil.copytree(src / "inputs", dst / "environment" / "inputs")
    for sub, shared in (case.get("shared_inputs") or {}).items():
        shutil.copytree(GENERIC / "inputs" / shared, dst / "environment" / "inputs" / sub,
                        dirs_exist_ok=True)

    # solution/: upstream oracle unchanged, wrapped.
    shutil.copytree(original / "solution", dst / "solution")
    (dst / "solution" / "solve.sh").rename(dst / "solution" / "solve_original.sh")
    (dst / "solution" / "solve.sh").write_text(SOLVE_SH, encoding="utf-8")
    (dst / "solution" / "solve.sh").chmod(0o755)
    shutil.copy2(LIB / "caebench_tn" / "oracle_finish.py", dst / "solution" / "tn_oracle_finish.py")
    solver = profile["domains"][case["domain"]]["solvers"][0]
    (dst / "solution" / "tn_oracle.json").write_text(json.dumps({
        "track": case["track"], "domain": case["domain"], "solver": solver,
        "entry": ORIGINAL_ENTRY[case["domain"]], "spec": spec,
        "kpi_names": kpi_names,
    }, indent=2), encoding="utf-8")

    # tests/: upstream files (kpis.json, spec.json, Dockerfile, compose, given/)
    # byte-for-byte, minus the upstream entry points; plus the TN verifier.
    shutil.copytree(original / "tests", dst / "tests",
                    ignore=shutil.ignore_patterns("test.sh", "verify.py", "verify_native.py", "__pycache__"))
    (dst / "tests" / "test.sh").write_text(TEST_SH, encoding="utf-8")
    (dst / "tests" / "test.sh").chmod(0o755)
    (dst / "tests" / "tn.json").write_text(json.dumps({
        "case_id": spec["case_id"], "profile": profile["name"], "track": case["track"],
        "domain": case["domain"], "solvers": profile["domains"][case["domain"]]["solvers"],
        "original_task": case["original"],
    }, indent=2), encoding="utf-8")
    if not profile.get("inherit_images", False):
        df = dst / "tests" / "Dockerfile"
        df.write_text(re.sub(r"(?m)^FROM .*$", f"FROM {profile['domains'][case['domain']]['verifier_image']}",
                             df.read_text(encoding="utf-8"), count=1), encoding="utf-8")
    # The same neutral inputs, for the verifier to put back at /tmp/agent/inputs
    # before the replay (the verifier container is a different container).
    if (dst / "environment" / "inputs").is_dir():
        shutil.copytree(dst / "environment" / "inputs", dst / "tests" / "inputs")
    vendor(dst / "tests")
    return dst


def write_coverage(profile: dict, rows: list[tuple[str, dict, bool, list[str]]]) -> Path:
    path = GENERIC / "coverage" / f"{profile['name']}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    covered = sum(1 for r in rows if r[2])
    lines = [
        f"# Coverage -- profile `{profile['name']}`",
        "",
        f"{VARIANT_NOTICE}",
        "",
        f"Profile status: **{profile.get('status', 'unknown')}**. {profile.get('label', '')}",
        "",
        f"{covered} of {len(rows)} neutral tasks covered.",
        "",
        "| task | domain | portability | covered | missing capabilities |",
        "|---|---|---|---|---|",
    ]
    for rel, case, ok, missing in rows:
        lines.append(f"| `{rel}` | {case['domain']} | {case['portability']} | {'yes' if ok else 'no'} | "
                     f"{', '.join(f'`{m}`' for m in missing) or '-'} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="caebench_tn.generate")
    ap.add_argument("--profile", required=True)
    ap.add_argument("--case", help="glob over <domain>/<sub>/<case> or a case name")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--force", action="store_true", help="render a stub profile anyway")
    args = ap.parse_args(argv)

    profile = load_toml(GENERIC / "profiles" / f"{args.profile}.toml")
    out_root = args.out or GENERIC / "dist" / profile["name"]
    render = profile.get("status") == "tested" or args.force

    rows = []
    rendered = 0
    for src in neutral_cases(args.case):
        case = load_toml(src / "case.toml")
        ok, missing = coverage(profile, case)
        rows.append((str(src.relative_to(GENERIC / "cases")), case, ok, missing))
        if ok and render:
            render_case(src, profile, out_root)
            rendered += 1
    if not args.case and args.out is None:
        print(f"coverage table: {write_coverage(profile, rows).relative_to(REPO)}")
    print(f"profile {profile['name']}: {len(rows)} neutral tasks, "
          f"{sum(r[2] for r in rows)} covered, {rendered} rendered"
          + ("" if render else " (stub profile: pass --force to render)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
