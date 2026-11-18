# Task — finish a constant-volume ignition run that was interrupted

A zero-dimensional ignition calculation was running on this machine and the
machine went down before it finished. Whatever the run had written by then is
in `/tmp/agent/run/`. Nothing else about it was recorded: there is no log, no
progress file, and no note of the conditions it was started at.

Pick the calculation up and finish it.

## What the calculation is

- A closed, spatially uniform, **constant-volume, adiabatic** reactor: a fixed
  volume of premixed methane/air with no heat loss, whose composition evolves
  under the chemistry of the mechanism GRI-Mech 3.0 (53 species, 325
  reactions), supplied in Chemkin format under `/tmp/agent/inputs/mechanism/`
  (`chem.inp`, `therm.dat`).
- **The operating point is whatever the interrupted run was at.** It is not
  stated here and it is not written down anywhere; the files in
  `/tmp/agent/run/` are the only record of it. Work it out from them.
- The interrupted run stopped during the induction period, before ignition.

## Output files

Write these into the submission root:

- **`results.csv`** — the raw numerical output of the **whole** calculation,
   written by `replay.sh` into the submission root, with a header row and
   these columns:
   - `time_s` — time in seconds, measured from the start of the original run
   - `T_K` — temperature in kelvin
   - `P_Pa` — pressure in pascal

   It must cover the run from its start through ignition and on until `dT/dt`
   has fallen below 0.1% of the maximum value it reached, so the trace covers
   the whole event and the relaxation after it.

   **The rows the interrupted run had already completed must come back
   unaltered** — same times, same values, in the same order, at the front of the
   file. The evaluator compares them against its own copy of the interrupted
   run, row by row and value by value, and a file that drops them, truncates
   their precision or reorders them fails whatever the physics says.

   Write every column at full numerical precision — do not round the values or
   format them to a fixed number of decimal places — and place the rows you add
   closely enough together that the ignition event is resolved by the file
   itself. The reported result is read off this file and nothing else, so it can
   be no sharper than the spacing between the rows on either side of the `dT/dt`
   maximum.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission containing only your source files **and the interrupted run's own files**, under a hard limit of **900 seconds**; a run that overruns is scored zero however good the physics. It strips every numeric artifact from its copy of your submission, then restores its own pristine copy of the interrupted run's files before re-running `replay.sh`, so nothing else you leave can affect the score.
