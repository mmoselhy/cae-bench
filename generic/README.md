# CAE-bench-TN — tool-neutral variant (unofficial)

> **Not CAE-bench.** CAE-bench-TN is an unofficial derivative of
> [svd-ai-lab/cae-bench](https://github.com/svd-ai-lab/cae-bench) (Apache-2.0; see
> [`NOTICE`](NOTICE) and [`../LICENSE`](../LICENSE)). Its scores are CAE-bench-TN
> scores and must not be reported as CAE-bench scores. Rendered task names use the
> namespace `caebench-tn/`.

The same 77 engineering-simulation tasks as CAE-bench, posed so that they can be
solved with whatever simulation tools a harness provides (open-source solvers,
Siemens, Altair; via CLI or MCP). `cases/` is untouched. Design:
[`../docs/generic/DESIGN.md`](../docs/generic/DESIGN.md).

## Layout

| path | what |
|---|---|
| `cases/<domain>/<sub>/<case>/` | neutral sources: `case.toml` (capabilities, portability label, link to the original), `prompt.md` (physics, conditions, required models, KPI table, budget), `env/<profile>.md` (task-specific tool facts), `inputs/` |
| `inputs/` | neutral inputs shared by many tasks: Chemkin mechanisms, cell parameter data sheets |
| `profiles/*.toml` | what each tool profile provides, its solvers and environment appendices |
| `lib/caebench_tn/` | contract, verifier core, solver adapters, generator, calibration, gates |
| `coverage/<profile>.md` | which tasks each profile covers |
| `dist/<profile>/` | rendered Harbor datasets (generated, not versioned) |
| `results/*.json` | gate digests; `PARITY.md` is built from them |
| `environment/` | local image build wrapper and a reconstructed `fem-fullstack` recipe |

## Use

```bash
cd generic/lib
python3 -m caebench_tn.generate --profile opensource          # -> generic/dist/opensource
harbor run -p ../dist/opensource/cfd/fluids/lid_driven_cavity_ghia_re1000 --agent oracle -y

python3 -m caebench_tn.gates run --set original|generic [-n 2]  # gates A / B
python3 -m caebench_tn.gates negatives                           # gate C (task level)
python3 -m caebench_tn.gates diff                                # gate D
python3 -m caebench_tn.gates parity                              # gate E -> PARITY.md

python3 -m caebench_tn.calibrate --profile P --task <rendered task> --submission <dir>
../scripts/agent_parity.sh ...   # COSTS API MONEY -- needs explicit approval
```

## The neutral contract

`/tmp/agent/submission/` must hold `replay.sh` (re-solves from a clean copy), the
task's output file(s), and `result.json`:

```json
{"solver": {"name": "openfoam", "version": "v2412"}, "replay": "replay.sh",
 "native_results": ["..."], "kpis": {"<kpi>": {"value": 0.0, "source": {"kind": "file_extract", "path": "...", "extract": "..."}}}}
```

The score is computed exactly as upstream computes it, from the output files the
evaluator regenerates by running `replay.sh`. The `kpis` claims are re-extracted
and recorded (`claim_audit` in `reward_detail.json`) but never scored.

## Verifier

Shared core (`core.py`): contract check → adapter selection → clean-copy replay
→ adapter's "a real solve happened" check → upstream KPI derivation and band
scoring (`score.py` unchanged). Adapters: `openfoam`, `calculix`, `cantera`,
`pybamm` wrap the upstream checks by import; `starccm`, `simcenter-nastran`,
`optistruct` are **untested stubs** that always report `unverified` (score 0).
An unknown solver is `unverified`, never a pass.

## Status

See [`PARITY.md`](PARITY.md) for the per-task gate results and
[`results/conversions/`](results/conversions) for the neutral-input proofs.
