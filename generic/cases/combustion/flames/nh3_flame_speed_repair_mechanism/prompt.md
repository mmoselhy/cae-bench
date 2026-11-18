# Task — an ammonia flame-speed setup that returns the wrong number

A setup handed over in your working directory computes the laminar burning
velocity of a premixed ammonia/air flame (the environment notes at the end of
this page say which file it is and what it is written for). It runs to
completion without error, it converges, and it writes a results file and a
figure — and the burning velocity it reports is well below the accepted value
for this mixture.

Find out why, fix it, and hand back a setup that produces the right answer.

## The operating point

| quantity | value |
|---|---|
| fuel | NH₃ (ammonia) |
| oxidiser | air, O₂:N₂ = 1:3.76 |
| equivalence ratio φ | 0.94 |
| unburned temperature | 328.0 K |
| pressure | 1.7 atm |

The flame is one-dimensional, freely propagating and premixed; the reported
quantity is the unburned-side velocity, i.e. the laminar burning velocity.

The operating point above is correct as written in the handed-over setup, and
so are the domain width, the transport model and the refinement criteria — the
solution is converged and grid-independent. The defect is a single modelling
choice made before any of that, and it is the kind of choice that produces a
clean run and a wrong answer rather than an error message.

## What to change

Whatever is needed for the setup to model *this* mixture. Do not change the
operating point, the fuel, or the oxidiser composition to move the answer —
those define what is being asked. Do not hard-code the burning velocity or
post-correct it; the number must come out of the solve.

Whatever you choose must be available in the installed distribution of the
evaluation environment (see the environment notes) — check what is there
rather than assuming, and confirm your choice is applicable to this fuel rather
than merely able to run with it. Several options will execute happily and still
be wrong, which is the trap this task is built around.

## Output files

Write these into the submission root:

- **`results.csv`** — the output of actually running the corrected setup,
   written by `replay.sh`, with a header row and the columns `grid_m`, `T_K`,
   `velocity_m_s`.

   Write every column at full numerical precision — do not round the values
   or format them to a fixed number of decimal places — and place the rows
   closely enough together that the quantity asked for above is resolved by
   the file itself. The reported result is read off this file and nothing
   else, so it can be no sharper than the spacing between the rows that
   determine it.
   For a speed read at the unburned edge of the profile, those are the rows
   nearest that edge.

Run `replay.sh` yourself and leave its output in the submission. The evaluator
also re-runs `replay.sh` from a clean copy and takes the number from *its* own
run, so nothing is gained by hand-editing `results.csv` — but the file and the
figure are part of what is asked for, and are checked for.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **900 seconds**; a run that overruns is scored zero however good the physics.

## Analytical-shortcut notice

There is no closed form for a laminar burning velocity — it depends on the
full kinetic mechanism, the transport model and the flame structure, so it can
only come from a solve. Recalling a literature value for ammonia and writing
it into the setup will not survive the evaluator's own re-run.
