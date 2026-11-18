# Pilot -- gates A-D on two tasks (CAE-bench-TN, opensource profile)

Unofficial tool-neutral variant of CAE-bench; these are oracle runs, not agent scores.
All runs: `harbor run --agent oracle` (Harbor 0.26.0, Docker 29.10), images built
locally with `generic/environment/build_local.sh` (upstream Dockerfiles; the
`sim-benchmark-fem-fullstack` image is a local reconstruction -- Ubuntu 22.04,
CalculiX 2.17-3, Gmsh 4.8.4 -- because upstream ships no recipe for it).

| gate | lid_driven_cavity_ghia_re1000 | pkg25d_thermal_tim118um_k4p7_h22600 |
|---|---|---|
| A  original oracle score | 1.0 | 1.0 |
| A  original KPIs | u_min = -0.38128992 | 99.42533 / 40.61384 / 38.4309 degC |
| B  generic oracle score | 1.0 | 1.0 |
| B  generic KPIs | u_min = -0.38128992 | 99.42533 / 40.61384 / 38.4309 degC |
| B  KPI difference (tolerance: rel 1e-9) | 0 (bit-identical) | 0 (bit-identical) |
| B  result.json claims re-extracted | P0 (upstream oracle never writes results.csv in place, so no claim; diagnostic only) | P4_pass, claim = evaluator value |
| C  empty submission | 0.0 (contract_invalid) | 0.0 (contract_invalid) |
| C  printf replay, valid contract | 0.0 (invalid_submission: no case inputs) | 0.0 (invalid_physics_setup: no .frd) |
| C  printf replay + real OpenFOAM inputs | 0.0 (invalid_physics_setup: no solved fields) | n/a |
| D  kpis.json / spec.json byte-identical | yes | yes |

Gate C, upstream unit tests: `lib/sim_benchmark_verifier/tests` gives the same
result with and without this branch's `lib/` change -- 443 passed, 7 skipped, and
the identical set of 32 failures/errors, all in `test_generator_emit_guards.py`
because `tools/gen_*_cases.py` is absent from the public repo (pre-existing).
Generic unit tests (`generic/lib/tests`): 20 passed.

Raw digests: `generic/results/{original,generic,neg_empty,neg_printf,gate_d}.json`.
