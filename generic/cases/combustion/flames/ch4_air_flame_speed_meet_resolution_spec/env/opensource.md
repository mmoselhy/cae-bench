- The handed-over setup is `run_case.py` in your working directory: a Cantera Python
  script that writes `results.csv` and a figure but no resolution table. It is a
  starting point, not the deliverable -- the evaluator runs `replay.sh`, which may
  simply run your corrected script (`python3 run_case.py`).
- The reaction mechanism is Cantera's `gri30.yaml`. It ships with the installed Cantera
  distribution and can be loaded by that exact string. The Chemkin files under
  `/tmp/agent/inputs/mechanism/` were exported from it with Cantera's `write_chemkin`.
