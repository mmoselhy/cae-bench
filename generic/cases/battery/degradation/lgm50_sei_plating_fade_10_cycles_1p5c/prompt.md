# Cycle ageing of an NMC811 / graphite-silicon cell parameterised for degradation

Determine how much capacity a lithium-ion cell loses over a run of full cycles once its ageing mechanisms are active.

## Cell and operating point

| quantity | value |
|---|---|
| cell | an NMC811 / graphite-silicon cell parameterised for degradation |
| parameter set | O'Kane et al. (2022): LG M50 NMC811 / graphite-SiOx cell, with degradation parameters; its parameter values are supplied as a tool-neutral data sheet, `/tmp/agent/inputs/parameters/cell.json` (scalars with units, functional dependences tabulated; the format is described in `README.md` beside it) |
| initial state of charge | 100% |
| ambient temperature | 288.15 K |
| degradation mechanisms | SEI: solvent-diffusion limited, lithium plating: partially reversible |

## Protocol

Simulate ten consecutive cycles at 288.15 K, each a 1.5C discharge to 2.5 V followed by a 1.5C charge to 4.2 V and a constant-voltage hold at 4.2 V until the current falls to 50 mA, with both solid-electrolyte-interphase growth and partially reversible lithium plating active so the cell ages as it cycles.

Model the cell with a physics-based electrochemical model that includes the
degradation mechanisms named above, so that the capacity the cell delivers
changes from cycle to cycle because lithium is being consumed, not because a
fade curve was imposed.

Measure the capacity of each cycle as the charge delivered during that cycle's
discharge phase, and report the loss from the first cycle to the last.

Represent each electrode by a **single representative particle**, while still
solving lithium transport in the electrolyte across the cell. (Resolving each
electrode through its thickness answers a slightly different question, so this
choice is part of the specification.)

Report the **capacity fade in percent — the last cycle's discharge capacity relative to the first cycle's, expressed as a percentage loss**.

## Output files

Write these into the submission root:

- **`results.csv`** — the raw numerical output of the run, written by `replay.sh`, with a header row and these columns:
   - `time_s` — time in seconds, increasing from 0
   - `current_A` — cell current in amperes, **positive when discharging**
   - `voltage_V` — terminal voltage in volts

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **900 seconds**; a run that overruns is scored zero however good the physics. How much refinement you can afford is therefore part of the problem.
