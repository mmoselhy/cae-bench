# CAE-bench-TN — design of the tool-neutral variant

**Status: implemented.** Results in [`generic/PARITY.md`](../../generic/PARITY.md); usage in [`generic/README.md`](../../generic/README.md). Sections below were written before the code and are annotated where the build changed them ("*Built:*").
CAE-bench-TN ("tool-neutral") is an **unofficial derivative** of
[svd-ai-lab/cae-bench](https://github.com/svd-ai-lab/cae-bench) (Apache-2.0).
Its scores are **not** CAE-bench scores and must never be reported as such.
Rendered task names use the namespace `caebench-tn/`, never `hwe-bench/`.

## 1. What is tool-specific today (verified by reading the code)

| layer | where it lives | what is solver-specific |
|---|---|---|
| prompt | `cases/*/instruction.md` | names the solver (OpenFOAM v2412, `ccx`+Gmsh, `gri30.yaml` "loadable by that string", PyBaMM `Chen2020`), the case layout (`0/ constant/ system/`), the deliverable name |
| deliverable | `Allrun` (cfd), `run_case.sh` (packaging), `run_case.py` run by `sys.executable` (combustion, battery) | entry-point name and interpreter are hard-coded in the four evaluators |
| interface | `results.csv` | **not** solver-specific: columns are physical quantities (`u_min_vertical_centerline`, `t_asic_max_c`, `time_s,T_K,P_Pa`, `time_s,current_A,voltage_V`). This is the part that already travels. |
| KPI derivation | `tests/spec.json` + `csv_interface.derive` / `native_cantera.extract_*` / `native_pybamm.extract_*` | **evaluator-owned** and solver-agnostic: it reads the CSV, never the solver's files |
| scoring | `score.band_score`, `pass_tol`, `_physics_pass`; `native_openfoam.band_verdict` | solver-agnostic |
| "a real solve happened" | `detectors.openfoam.has_mesh_and_solution` (serialised polyMesh + solved time dir), `detectors.calculix.has_result_database` (.frd holding the model), strip rules (`is_generated`, `GENERATED_SUFFIXES`, `is_reproduction_input`) | solver-specific — this is what adapters wrap |
| physics gates | Cantera `equilibrium_consistent` (diagnostic), `initial_state_valid`; PyBaMM `ocv_consistent` (gate) | computed **by the verifier** from the mechanism / parameter set, independent of which tool the agent used. They need Cantera/PyBaMM *in the verifier image*, not in the agent's. |
| inputs | supplied `constant/polyMesh` (`naca0012_subsonic`, `bump_in_channel_2d` via `preserve`), `gri30.yaml` & other mechanisms, PyBaMM parameter sets by name | native formats only |
| repair / resume | `channel_retau395_repair_closure`, `nh3_flame_speed_repair_mechanism`, `ch4_air_idt_resume_interrupted_run` (plants evaluator-owned `given/` files) | the task *is* a native file |

Two facts shape everything below. (a) The original verifiers **do not read
`result.json`** at all: they replay the entry point from a clean copy and
derive the KPIs themselves from `results.csv`. (b) `score.py`'s
`file_extract` path is the only place `result.json` claims are checked, and
the live tracks don't use it.

## 2. Layout

```
cases/                      untouched (gate D diffs it)
generic/
  cases/<domain>/<sub>/<case>/
      task.neutral.toml     capabilities, portability label, timeouts, link to original case
      prompt.md             physics, conditions, required models, KPI table, budget
      inputs/               neutral inputs (+ native originals, kept byte-identical)
  profiles/<profile>.toml   provides=[caps], env appendix per domain, images, adapter ids
  lib/caebench_tn/          verifier core + adapters + generator + calibration
  dist/<profile>/           generated Harbor datasets (gitignored except coverage.md)
  PARITY.md                 gate E
```

`tests/kpis.json` and `tests/spec.json` are **not copied into generic/cases**;
the generator copies them from `cases/` at render time and gate D asserts
byte equality, so a reference value or band cannot drift by construction.

## 3. Neutral prompt + profile appendix

`prompt.md` = the original instruction with tool names, file layouts and
commands removed, keeping the physics, the required model (e.g. "single
particle model with electrolyte", "laminar steady incompressible"), the KPI /
CSV-column table and the time budget. The generator appends the neutral output
contract (§4) and then the profile's appendix for the task's domain. For the
`opensource` profile the appendix restates **every environment fact** in the
original prompt (solver + version, "`gri30.yaml` loadable by that string",
"`ccx` and Gmsh on PATH", the `Chen2020` name, the "rerun must leave the
solver's own result output behind" warning). A render-time check diffs the set
of tool tokens in original vs rendered-opensource prompts and fails on any loss.

## 4. Neutral output contract (`/tmp/agent/submission/`)

- `replay.sh` — non-interactive; from a clean copy holding only sources and
  inputs it re-solves and rewrites the interface file; non-zero on failure;
  must finish in the original case's `reproduction_timeout_s`.
- `results.csv` — **unchanged columns** from the original (this is what keeps
  derivation identical).
- `result.json` — `{"solver": {"name", "version"}, "replay": "replay.sh",
  "native_results": [paths], "kpis": {<kpi>: {"value", "source": {"kind":
  "file_extract", "path", "extract"}}}}`.
- figure where the original requires one (combustion, battery).

The **score comes from the evaluator's own derivation over the replayed
`results.csv`**, exactly as today. The `result.json` KPI claims are re-extracted
against the replayed copy and recorded as `provenance_stage` (diagnostic, not
scored) — making them scored would change scores vs. the original (gate B).

## 5. Verifier: shared core + per-solver adapters

```
core:  validate contract → copy to temp → adapter.strip() + neutral strip
       → run replay.sh under budget → adapter.solver_evidence(workdir)
       → domain physics gates (OCV / initial state / equilibrium; verifier-side)
       → derive KPIs from results.csv (existing spec.json derivations)
       → score with existing functions (score.py untouched)
```

Adapter interface: `name`, `strip(workdir)`, `solver_evidence(workdir) ->
{"verdict": pass|fail|unverified, "detail"}`. Selection by
`result.json.solver.name`; an unknown or stub solver yields
`verdict="unverified"` and **final score 0** with
`failure_category="unverified_solver"` — never a pass.

- `openfoam`, `calculix`, `cantera`, `pybamm`: wrap the existing predicates and
  strip rules by import, not by copy.
- **Parity mechanism (decision).** The cleanest way to give identical scores
  is to run the *same* evaluator functions. The four `main_from_case`
  entry points hard-code `Allrun` / `run_case.sh` / `run_case.py`. I will add one
  optional, default-preserving parameter (entry-point command) to those four
  call sites in `lib/` — no change to any check, threshold or `score.py`; the
  existing test suite must stay identical. Rejected alternative: re-implement
  the lifecycles in the core (divergence risk), or plant a `run_case.py` shim
  that calls `replay.sh` (passes, but is a hack that hides the contract).
- `starccm`, `simcenter_nastran`, `optistruct`: **stubs** returning
  `unverified`, each with a TODO naming the artifact it should check
  (`.sim`, `.op2`/`.f06`, `.h3d`/`.out`) — no parsing written, since none can be tested here.

## 6. Capabilities, portability, coverage

Each task declares `requires = [...]`, e.g. `cfd.incompressible.laminar.steady`,
`cfd.rans.sa`, `mesh.import.cgns`, `fea.thermal.steady`, `fea.thermomech.static`,
`kinetics.0d.const_volume`, `flame.1d.freely_propagating`,
`echem.spme`/`echem.dfn`, `thermal.lumped`, `aging.sei`. Profiles list
`provides`. The generator skips uncovered tasks and writes
`dist/<profile>/coverage.md`.

Portability label (with reason): `portable` (physics fully specified, inputs
convertible); `portable-after-calibration` (reference is the oracle's own
output and other discretisations could legitimately sit outside a 5% band —
most packaging & battery KPIs); `native-only` (the three repair/resume tasks;
tasks whose reference depends on a native parameter/mechanism file a tool
cannot read). Native-only tasks are still rendered for `opensource`.

*Built:* the four tested adapters are as described. For the trace tracks the
evaluator's own gates (clean reproduction, artifact, initial state, and for
PyBaMM the OCV check) are the evidence -- upstream has no solver-file gate
there, and none was added. The verifier also puts the task's neutral inputs
back at `/tmp/agent/inputs` (from `tests/inputs`, never from the submission)
before the replay, because the verifier runs in a different container and a
non-native replay needs them.

## 7. Neutral inputs

polyMesh → Gmsh `.msh` (and CGNS via meshio where patches survive); YAML
mechanisms → Chemkin (`ck2yaml`'s inverse: Cantera `write_chemkin`);
PyBaMM sets → BPX JSON where `pybamm.ParameterValues.create_from_bpx`
round-trips, else a documented JSON dump marked "not BPX". Each conversion is
proven by solving the oracle **from the neutral file** and comparing KPIs to the
native-input oracle (same tolerance as gate B); a conversion that fails is shipped
only with the native original and noted.

*Built:* (a) **BPX is not produced**: PyBaMM 26.7.1.0 can read BPX but has no
writer, and the `bpx` package is absent from the image. The neutral battery file
is instead a tabulated data sheet (`caebench-tn-cell-datasheet-v1`: scalars with
units, every functional parameter tabulated on stated grids), proven by
re-solving every battery oracle from it. It is an interpolation, so the proof
measures a small KPI difference rather than floating-point identity; see
`generic/results/conversions/battery.json`. Measured: all 35 KPIs of the 34 battery tasks stay inside their bands; largest shift 0.22 band widths (SEI+plating capacity fade), next 0.15 (Ecker rate-capacity loss, after geometric sto grids fixed a 32 mV OCP error near sto=0). (b) Mechanisms: Chemkin via
`write_chemkin`, proven by `ck2yaml` back and re-solving the oracle: 19/21 tasks, all inside the band, largest shift 0.014 band widths; the two native-only tasks (mechanism repair, resume from planted partial output) have no single-file oracle to redirect and keep their native inputs. (c) Meshes:
MSH 2.2 written directly from the polyMesh (CGNS skipped: meshio's CGNS writer
carries no boundary patches), proven by `gmshToFoam` back and a Harbor oracle run
on the round-tripped grid: naca0012 and bump both score 1.0, KPIs within 3e-8 rel. (the precision printed in results.csv). Native originals are always kept, and the
`opensource` profile keeps using them, so no conversion can move a parity score.

## 8. Calibration tool

`caebench_tn calibrate --profile P --case C --submission DIR` runs the core
verifier on a human reference submission and writes
`generic/calibration/<P>/<C>.json`: per-KPI value, `gt_value`, `pass_tol`,
inside/outside. It never writes to `kpis.json`.

## 9. Equivalence gates

- **A** — run `harbor run --agent oracle` on all 77 originals; save per-KPI
  values + scores to `generic/results/original.json`.
- **B** — render `opensource`, run the oracles adapted to the contract (their
  existing solve plus a `replay.sh` that calls the original entry point and a
  `result.json` writer). Pass iff score identical and every KPI satisfies
  `|a−b| ≤ 1e-9·max(1,|a|)` (rel. 1e-9; the oracles are deterministic per
  ORACLE.md). Any larger difference is reported, not absorbed.
- **C** — empty submission < 0.5; a `replay.sh` that only `printf`s the
  reference values scores 0; `lib/sim_benchmark_verifier/tests` unchanged.
  *Pre-existing upstream state, measured 2026-11-18:* 443 passed, 7 skipped,
  3 failed + 29 errors, **all** in `test_generator_emit_guards.py` because
  `tools/gen_*_cases.py` is not in the public repo. Gate C = this exact set.
- **D** — byte diff of every `kpis.json` and band field vs `cases/`.
- **E** — `generic/PARITY.md`, one row per task.
- Agent-level parity script (`generic/scripts/agent_parity.sh`) is written but
  **not run** without explicit approval (it spends API money).

*Measured (2026-11-18, all 77 tasks; digests in `generic/results/`):* A — 77/77
score 1.0. B — 77/77 score 1.0, all 97 KPIs bit-identical (worst rel. diff 0).
C — empty 0 and printf-replay 0 on all 77; `lib/sim_benchmark_verifier/tests`
the same 443/7/32 set as above; `generic/lib/tests` 21 passed. D — 154/154
files byte-identical, `cases/` clean. E — `generic/PARITY.md`.
Three upstream oracles (`flatplate_zpg_subsonic`, `channel_retau395_repair_closure`,
`turbulent_channel_flow_retau590`) exit non-zero in the agent phase (OpenFOAM
bashrc under `set -u`) yet leave a complete case that the evaluator replays to
1.0; the TN wrapper therefore keeps the upstream exit code and still writes the
contract whenever a submission exists.

## 10. Environment prerequisites

Gates A–C need a running Docker daemon, Harbor (`uv tool install harbor`),
and the images `sim-benchmark-{cfd,combustion,battery}-fullstack`,
`sim-benchmark-openfoam-verifier-v22:local` and
`sim-benchmark-fem-fullstack:latest`. **The repository has no Dockerfile or
build target for `fem-fullstack`** (`build.sh` knows only cfd/combustion/
battery); the packaging pilot needs it supplied or a documented recipe.

*Built:* `generic/environment/build_local.sh` builds the upstream Dockerfiles
unchanged behind an HTTPS-intercepting proxy (adds the proxy CA for the build
only, removes it in the last layer). `generic/environment/fem/Dockerfile` is a
**local reconstruction** of `fem-fullstack`: Ubuntu 22.04, `calculix-ccx`
2.17-3 (the version every packaging `kpis.json` records), Gmsh 4.8.4, the
shared harness. Gate A on it is the evidence that it reproduces the stored
references; it is not the image upstream used.
