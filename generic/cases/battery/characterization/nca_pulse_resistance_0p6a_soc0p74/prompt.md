# Pulse resistance measurement of a nickel-cobalt-aluminium / graphite cell

Determine the resistance a lithium-ion cell presents to a short discharge pulse applied from rest.

## Cell and operating point

| quantity | value |
|---|---|
| cell | a nickel-cobalt-aluminium / graphite cell |
| parameter set | Kim et al. (2011): NCA / graphite cell; its parameter values are supplied as a tool-neutral data sheet, `/tmp/agent/inputs/parameters/cell.json` (scalars with units, functional dependences tabulated; the format is described in `README.md` beside it) |
| initial state of charge | 74% |
| ambient temperature | 298.15 K |


## Protocol

Simulate a 15 second, 0.6 A discharge pulse applied from rest at 74% state of charge, preceded by a 400 second rest and followed by a 600 second relaxation.

Model the cell with a physics-based electrochemical model that resolves
transport in the electrolyte and in the particles, so that the voltage step at
the start of the pulse is produced by the model rather than imposed.

The quantity asked for is the **instantaneous** pulse resistance: the voltage
step across the current step at the beginning of the pulse, divided by the
size of that current step. It is not the resistance inferred from the end of
the pulse, which also contains diffusion.

Represent each electrode by a **single representative particle**, while still
solving lithium transport in the electrolyte across the cell. (Resolving each
electrode through its thickness answers a slightly different question, so this
choice is part of the specification.)

Report the **pulse resistance in ohms**.

## Output files

Write these into the submission root:

- **`results.csv`** — the raw numerical output of the run, written by `replay.sh`, with a header row and these columns:
   - `time_s` — time in seconds, increasing from 0
   - `current_A` — cell current in amperes, **positive when discharging**
   - `voltage_V` — terminal voltage in volts

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **600 seconds**; a run that overruns is scored zero however good the physics. How much refinement you can afford is therefore part of the problem.
