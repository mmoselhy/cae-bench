# Constant-current / constant-voltage charge of an NMC / graphite pouch cell

Determine how long it takes to recharge a partially discharged lithium-ion cell on a constant-current / constant-voltage schedule.

## Cell and operating point

| quantity | value |
|---|---|
| cell | an NMC / graphite pouch cell |
| parameter set | Mohtat et al. (2020): NMC532 / graphite pouch cell; its parameter values are supplied as a tool-neutral data sheet, `/tmp/agent/inputs/parameters/cell.json` (scalars with units, functional dependences tabulated; the format is described in `README.md` beside it) |
| initial state of charge | 23% |
| ambient temperature | 298.15 K |


## Protocol

Simulate a constant-current charge at 1.3C from 23% state of charge up to 4.2 V, followed by a constant-voltage hold at 4.2 V until the current falls to 40 mA.

Model the cell with a physics-based electrochemical model that resolves
transport in the electrolyte and in the particles. The transition from the
constant-current phase to the constant-voltage hold must come out of the
simulation reaching the voltage limit, not out of a prescribed time.

Resolve each electrode **through its thickness**, so that reaction rate,
potential and lithium concentration vary across the electrode rather than only
within a single representative particle. (Collapsing each electrode onto one
representative particle answers a slightly different question, so this choice
is part of the specification.)

Report the **total charge time in seconds — from the start of the constant-current phase to the end of the constant-voltage hold**.

## Output files

Write these into the submission root:

- **`results.csv`** — the raw numerical output of the run, written by `replay.sh`, with a header row and these columns:
   - `time_s` — time in seconds, increasing from 0
   - `current_A` — cell current in amperes, **positive when discharging**
   - `voltage_V` — terminal voltage in volts

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **600 seconds**; a run that overruns is scored zero however good the physics. How much refinement you can afford is therefore part of the problem.
