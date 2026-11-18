- The interrupted run was a Cantera run. The mechanism it used is Cantera's
  `gri30.yaml`, which ships with the installed Cantera distribution and can be loaded
  by that exact string. The Chemkin files under `/tmp/agent/inputs/mechanism/` were
  exported from it with Cantera's `write_chemkin`.
- In the evaluator's re-run, its pristine copies of the interrupted run's files are
  restored at the root of the working copy, beside `replay.sh`, under the names they
  carry in `/tmp/agent/run/` (`results.csv`, `state.csv`); `replay.sh` runs from that
  directory. A `results.csv` you leave in the submission is replaced by the handover
  before the re-run, and `replay.sh` must overwrite it with the finished trace.
