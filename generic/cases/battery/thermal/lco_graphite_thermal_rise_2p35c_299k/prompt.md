# Discharge with cell heating of a lithium-cobalt-oxide / graphite cell

Determine how hot a lithium-ion cell gets when it is discharged at a fixed rate down to its cut-off voltage.

## Cell and operating point

| quantity | value |
|---|---|
| cell | a lithium-cobalt-oxide / graphite cell |
| parameter set | Ai et al. (2020): LCO / graphite pouch cell (Enertech); its parameter values are supplied as a tool-neutral data sheet, `/tmp/agent/inputs/parameters/cell.json` (scalars with units, functional dependences tabulated; the format is described in `README.md` beside it) |
| initial state of charge | 100% |
| ambient temperature | 299.15 K |


## Protocol

Simulate a constant-current discharge at 2.35C from a full charge, stopped when the terminal voltage first reaches 3.0 V, with the cell free to heat up.

Model the cell with a physics-based electrochemical model coupled to a
**lumped** thermal model: a single cell-averaged temperature, driven by the
irreversible and reversible heat generated inside the cell and cooled to the
ambient through the cell's surface. A spatially resolved thermal model answers
a different question and is not what is asked for here. Resolve the
discretisation well enough that the reported number is grid-converged.

Report the cell-averaged temperature, not a surface or hot-spot value.

Represent each electrode by a **single representative particle**, while still
solving lithium transport in the electrolyte across the cell. (Resolving each
electrode through its thickness answers a slightly different question, so this
choice is part of the specification.)

Report the **peak temperature rise in kelvin — the maximum cell-averaged temperature reached, minus the temperature at the start**.

## Output files

Write these into the submission root:

- **`results.csv`** — the raw numerical output of the run, written by `replay.sh`, with a header row and these columns:
   - `time_s` — time in seconds, increasing from 0
   - `current_A` — cell current in amperes, **positive when discharging**
   - `voltage_V` — terminal voltage in volts
   - `temperature_K` — cell-averaged temperature in kelvin

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **600 seconds**; a run that overruns is scored zero however good the physics. How much refinement you can afford is therefore part of the problem.
