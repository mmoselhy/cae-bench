# Rate capability of a lithium-ion cell with a graphite negative electrode

Determine how much of a lithium-ion cell's deliverable capacity is lost when it is discharged faster.

## Cell and operating point

| quantity | value |
|---|---|
| cell | a lithium-ion cell with a graphite negative electrode |
| parameter set | Ecker et al. (2015): Kokam NMC / graphite pouch cell; its parameter values are supplied as a tool-neutral data sheet, `/tmp/agent/inputs/parameters/cell.json` (scalars with units, functional dependences tabulated; the format is described in `README.md` beside it) |
| initial state of charge | 100% |
| ambient temperature | 292.15 K |


## Protocol

Simulate two constant-current discharges from a full charge, the first at 0.84C and the second at 2.52C, each stopped when the terminal voltage first reaches 2.5 V, with a constant-current constant-voltage recharge to 4.2 V between them.

Model the cell with a physics-based electrochemical model — one that resolves
lithium transport in the electrolyte and in the active-material particles, so
that the rate dependence of the delivered capacity comes out of the transport
solution rather than out of a fitted resistance.

Both discharges and the recharge between them belong to **one run**, written to
one output file, so the second discharge starts from the state the recharge
left the cell in. Resolve the discretisation well enough that the reported
number is grid-converged.

Represent each electrode by a **single representative particle**, while still
solving lithium transport in the electrolyte across the cell. (Resolving each
electrode through its thickness answers a slightly different question, so this
choice is part of the specification.)

Report the **rate capacity loss in per cent — the charge delivered by the first (lower-rate) discharge minus the charge delivered by the second (higher-rate) one, divided by the first**.

## Output files

Write these into the submission root:

- **`results.csv`** — the raw numerical output of the run, written by `replay.sh`, with a header row and these columns:
   - `time_s` — time in seconds, increasing from 0
   - `current_A` — cell current in amperes, **positive when discharging**
   - `voltage_V` — terminal voltage in volts

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **900 seconds**; a run that overruns is scored zero however good the physics. How much refinement you can afford is therefore part of the problem.
