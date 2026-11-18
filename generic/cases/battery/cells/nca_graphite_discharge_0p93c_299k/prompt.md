# Constant-current discharge of a nickel-cobalt-aluminium / graphite cell

Determine how much a lithium-ion cell delivers when it is discharged at a fixed rate down to its cut-off voltage.

## Cell and operating point

| quantity | value |
|---|---|
| cell | a nickel-cobalt-aluminium / graphite cell |
| parameter set | Kim et al. (2011): NCA / graphite cell; its parameter values are supplied as a tool-neutral data sheet, `/tmp/agent/inputs/parameters/cell.json` (scalars with units, functional dependences tabulated; the format is described in `README.md` beside it) |
| initial state of charge | 100% |
| ambient temperature | 299.15 K |


## Protocol

Simulate a constant-current discharge at 0.93C from a full charge, stopped when the terminal voltage first reaches 2.7 V.

Model the cell with a physics-based electrochemical model — one that resolves
lithium transport in the electrolyte and in the active-material particles, so
that the rate dependence of the delivered capacity comes out of the transport
solution rather than out of a fitted resistance. Resolve the discretisation
well enough that the reported number is grid-converged.

Represent each electrode by a **single representative particle**, while still
solving lithium transport in the electrolyte across the cell. (Resolving each
electrode through its thickness answers a slightly different question, so this
choice is part of the specification.)

Report the **discharge capacity in ampere-hours — the charge delivered over the discharge**.

## Output files

Write these into the submission root:

- **`results.csv`** — the raw numerical output of the run, written by `replay.sh`, with a header row and these columns:
   - `time_s` — time in seconds, increasing from 0
   - `current_A` — cell current in amperes, **positive when discharging**
   - `voltage_V` — terminal voltage in volts

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **600 seconds**; a run that overruns is scored zero however good the physics. How much refinement you can afford is therefore part of the problem.
