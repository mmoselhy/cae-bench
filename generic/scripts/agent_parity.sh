#!/usr/bin/env bash
# Agent-level parity: the SAME model and agent on original vs. generic tasks.
#
#   *** THIS SPENDS API MONEY. Do not run it without the owner's explicit OK. ***
#
#   generic/scripts/agent_parity.sh --model <model-id> [--agent terminus-2] \
#       [--tasks "cfd/fluids/lid_driven_cavity_ghia_re1000 packaging/thermal/pkg25d_thermal_tim118um_k4p7_h22600"] \
#       [--attempts 3] --i-understand-this-costs-money
#
# Runs each listed task twice per attempt -- once from cases/ (original) and once
# from generic/dist/opensource/ (rendered) -- and writes a side-by-side table to
# generic/results/agent_parity_<model>.md. `terminus-2` is the scaffold the
# official board uses; anything else is a diagnostic.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AGENT=terminus-2; MODEL=""; ATTEMPTS=3; OK=0
TASKS="cfd/fluids/lid_driven_cavity_ghia_re1000 packaging/thermal/pkg25d_thermal_tim118um_k4p7_h22600"
while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="$2"; shift 2;;
    --agent) AGENT="$2"; shift 2;;
    --tasks) TASKS="$2"; shift 2;;
    --attempts) ATTEMPTS="$2"; shift 2;;
    --i-understand-this-costs-money) OK=1; shift;;
    *) echo "unknown arg $1" >&2; exit 2;;
  esac
done
[ -n "$MODEL" ] || { echo "--model is required" >&2; exit 2; }
[ "$OK" = 1 ] || { echo "refusing to run: pass --i-understand-this-costs-money" >&2; exit 3; }

JOBS="$REPO/generic/results/agent_jobs"
mkdir -p "$JOBS"
safe_model="$(echo "$MODEL" | tr '/: ' '___')"
for t in $TASKS; do
  for set in original generic; do
    if [ "$set" = original ]; then p="$REPO/cases/$t"; else p="$REPO/generic/dist/opensource/$t"; fi
    harbor run -p "$p" -a "$AGENT" -m "$MODEL" -k "$ATTEMPTS" -y -q \
      -o "$JOBS" --job-name "${set}__${safe_model}__$(echo "$t" | tr / _)"
  done
done

python3 - "$JOBS" "$safe_model" "$REPO/generic/results/agent_parity_${safe_model}.md" <<'EOF'
import json, sys
from pathlib import Path
jobs, model, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
rows = {}
for job in jobs.glob(f"*__{model}__*"):
    s, _, task = job.name.split("__", 2)
    scores = []
    for trial in job.iterdir():
        r = trial / "verifier" / "reward.json"
        if r.is_file():
            scores.append(json.loads(r.read_text())["score"])
    rows.setdefault(task, {})[s] = scores
lines = [f"# Agent parity -- {model}", "", "| task | original scores | generic scores | mean diff |", "|---|---|---|---|"]
for task, d in sorted(rows.items()):
    a, b = d.get("original", []), d.get("generic", [])
    md = (sum(b)/len(b) - sum(a)/len(a)) if a and b else float("nan")
    lines.append(f"| {task} | {a} | {b} | {md:+.3f} |")
out.write_text("\n".join(lines) + "\n"); print(out)
EOF
