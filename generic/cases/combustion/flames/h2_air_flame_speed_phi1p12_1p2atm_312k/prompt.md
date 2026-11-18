# Laminar flame speed of hydrogen/air at phi=1.12, 1.2 atm

Determine how fast a premixed laminar flame propagates into this unburned fuel/air mixture.

## Conditions

| quantity | value |
|---|---|
| fuel | hydrogen (H2 in the mechanism) |
| oxidizer | air, modelled as O2 : N2 = 1 : 3.76 by mole |
| equivalence ratio | 1.12 |
| unburned-gas temperature | 312 K |
| pressure | 1.2 atm |
| reaction mechanism | the 10-species hydrogen/oxygen mechanism derived from GRI-Mech 3.0 (H2/O2 subset with Ar); supplied in Chemkin format under `/tmp/agent/inputs/mechanism/` (`chem.inp`, `therm.dat`, `tran.dat`) |

Consider a **freely propagating, one-dimensional, adiabatic premixed laminar
flame** in this mixture: a planar flame stabilised in a uniform incoming
stream of the unburned gas at the stated temperature and pressure.

Report the **unstretched laminar flame speed**, i.e. the velocity of the
unburned mixture entering the flame. Use the **mixture-averaged** transport
model (a multicomponent treatment gives a slightly different answer, so this
choice is part of the specification). Resolve the flame well enough that the
reported speed is grid-converged.

## Output files

Write these into the submission root:

- **`results.csv`** — the raw numerical output of the run, written by `replay.sh`, with a header row and these columns:
   - `grid_m` — position across the flame in metres
   - `T_K` — temperature in kelvin
   - `velocity_m_s` — axial velocity in metres per second

   Write every column at full numerical precision — do not round the values
   or format them to a fixed number of decimal places — and place the rows
   closely enough together that the quantity asked for above is resolved by
   the file itself. The reported result is read off this file and nothing
   else, so it can be no sharper than the spacing between the rows that
   determine it.
   For a speed read at the unburned edge of the profile, those are the rows
   nearest that edge.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **900 seconds**; a run that overruns is scored zero however good the physics. How much refinement you can afford is therefore part of the problem.
