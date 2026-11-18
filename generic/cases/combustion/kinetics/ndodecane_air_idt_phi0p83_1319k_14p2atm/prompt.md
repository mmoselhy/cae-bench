# Ignition delay of n-dodecane/air at 1319 K and 14.2 atm

Determine how long a premixed fuel/air mixture takes to autoignite after being brought instantaneously to the stated conditions.

## Conditions

| quantity | value |
|---|---|
| fuel | n-dodecane (c12h26 in the mechanism) |
| oxidizer | air, modelled as O2 : N2 = 1 : 3.76 by mole |
| equivalence ratio | 0.83 |
| initial temperature | 1319 K |
| pressure | 14.2 atm |
| reaction mechanism | the reduced 100-species n-dodecane mechanism of Reitz and co-workers; supplied in Chemkin format under `/tmp/agent/inputs/mechanism/` (`chem.inp`, `therm.dat`) |

Treat the mixture as a spatially uniform, **constant-volume, adiabatic**
system: it is a closed reactor of fixed volume with no heat loss, initially
at the stated temperature and pressure, whose composition then evolves under
the chemistry of the given mechanism.

Report the **ignition delay time**, defined as the time at which the rate of
temperature rise dT/dt reaches its maximum. Integrate past ignition until
dT/dt has fallen below 0.1% of the maximum value it reached, so the trace
covers the whole event and the relaxation after it.

## Output files

Write these into the submission root:

- **`results.csv`** — the raw numerical output of the run, written by `replay.sh`, with a header row and these columns:
   - `time_s` — time in seconds, increasing from 0
   - `T_K` — temperature in kelvin
   - `P_Pa` — pressure in pascal

   Write every column at full numerical precision — do not round the values
   or format them to a fixed number of decimal places — and place the rows
   closely enough together that the quantity asked for above is resolved by
   the file itself. The reported result is read off this file and nothing
   else, so it can be no sharper than the spacing between the rows that
   determine it.
   For a delay defined by the dT/dt maximum, those are the rows on either
   side of that maximum.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **900 seconds**; a run that overruns is scored zero however good the physics. How much refinement you can afford is therefore part of the problem.
