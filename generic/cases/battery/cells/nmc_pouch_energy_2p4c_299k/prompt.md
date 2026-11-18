# Constant-current discharge of an NMC / graphite pouch cell

Determine how much a lithium-ion cell delivers when it is discharged at a fixed rate down to its cut-off voltage.

## Cell and operating point

| quantity | value |
|---|---|
| cell | an NMC / graphite pouch cell |
| parameter set | Mohtat et al. (2020): NMC532 / graphite pouch cell; its parameter values are supplied as a tool-neutral data sheet, `/tmp/agent/inputs/parameters/cell.json` (scalars with units, functional dependences tabulated; the format is described in `README.md` beside it) |
| initial state of charge | 100% |
| ambient temperature | 299.15 K |


## Protocol

Simulate a constant-current discharge at 2.4C from a full charge, stopped when the terminal voltage first reaches 2.8 V.

Model the cell with a physics-based electrochemical model — one that resolves
lithium transport in the electrolyte and in the active-material particles, so
that the rate dependence of the delivered capacity comes out of the transport
solution rather than out of a fitted resistance. Resolve the discretisation
well enough that the reported number is grid-converged.

Resolve each electrode **through its thickness**, so that reaction rate,
potential and lithium concentration vary across the electrode rather than only
within a single representative particle. (Collapsing each electrode onto one
representative particle answers a slightly different question, so this choice
is part of the specification.)

Report the **discharge energy in watt-hours — the energy delivered over the discharge**.

## Output files

Write these into the submission root:

- **`results.csv`** — the raw numerical output of the run, written by `replay.sh`, with a header row and these columns:
   - `time_s` — time in seconds, increasing from 0
   - `current_A` — cell current in amperes, **positive when discharging**
   - `voltage_V` — terminal voltage in volts

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **600 seconds**; a run that overruns is scored zero however good the physics. How much refinement you can afford is therefore part of the problem.
