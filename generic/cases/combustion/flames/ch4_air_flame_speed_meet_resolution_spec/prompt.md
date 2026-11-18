# Task — a flame-speed setup that does not meet the resolution requirement

A setup handed over in your working directory computes the laminar burning
velocity of a premixed methane/air flame (the environment notes at the end of
this page say which file it is and what it is written for). It runs to
completion without error, the solver reports success, and it writes a results
file and a figure.

**It does not meet the requirement stated under "The requirement" below.**
Bring it up to that requirement and report the burning velocity that comes out
of the setup that does. (If your toolchain cannot run the handed-over setup,
treat it as the description of a setup that misses the requirement and build
your own; the requirement and the deliverables are the same either way.)

## The operating point

| quantity | value |
|---|---|
| fuel | methane (CH4 in the mechanism) |
| oxidizer | air, modelled as O2 : N2 = 1 : 3.76 by mole |
| equivalence ratio | 1.07 |
| unburned-gas temperature | 312 K |
| pressure | 1.2 atm |
| reaction mechanism | GRI-Mech 3.0 (53 species, 325 reactions); supplied in Chemkin format under `/tmp/agent/inputs/mechanism/` (`chem.inp`, `therm.dat`, `tran.dat`) |

The flame is **freely propagating, one-dimensional, adiabatic and premixed**:
a planar flame stabilised in a uniform incoming stream of the unburned gas at
the stated temperature and pressure. The reported quantity is the
**unstretched laminar burning velocity**, i.e. the velocity of the unburned
mixture entering the flame. Use the **mixture-averaged** transport model (a
multicomponent treatment gives a slightly different answer, so this choice is
part of the specification).

None of the above may be changed to move the answer — the operating point,
the fuel, the oxidizer composition, the mechanism and the transport model are
what is being asked about. Everything else about how the calculation is set up
and resolved is yours to choose.

## The requirement

The burning velocity you report has to have **stopped moving under further
resolution**, and you have to show that from your own runs rather than assert
it. Concretely, the table you submit must satisfy all four of these:

1. it holds **at least 3 rows**, each at a different resolution;
2. the finest row resolves the flame with **at least twice** as many grid
   points as the coarsest row;
3. **each of the last two refinement steps** changes the burning velocity by
   **no more than 2%** — one small step is not enough, because a value can
   stop moving for a single step without having converged;
4. the burning velocity you report agrees with the **finest** row of the table
   to within **2%** — the table has to be about the run you are reporting.

Nothing here says which setting to change to satisfy it, and that is
deliberate: how you resolve the flame is one of the free choices above.

## Output files

Write these into the submission root. `replay.sh` must perform the whole
calculation, including every row of the table.

- **`results.csv`** — the raw numerical output of the run you are reporting,
   written by `replay.sh`, with a header row and these columns:
   - `grid_m` — position across the flame in metres
   - `T_K` — temperature in kelvin
   - `velocity_m_s` — axial velocity in metres per second

   Write every column at full numerical precision — do not round the values or
   format them to a fixed number of decimal places — and place the rows closely
   enough together that the quantity asked for above is resolved by the file
   itself. The reported result is read off this file and nothing else, so it
   can be no sharper than the spacing between the rows that determine it. For a
   speed read at the unburned edge of the profile, those are the rows nearest
   that edge.

- **`grid_independence.csv`** — the table the requirement above is judged on,
   also written by `replay.sh`, with a header row and these columns:
   - `n_grid_points` — how many grid points that solution ended up with
   - `flame_speed_cm_s` — the burning velocity from that solution, in
     centimetres per second

   One row per resolution, in any order. `n_grid_points` is an outcome of the
   run, not a setting you are asked to declare: whatever you did to resolve the
   flame more finely, report the grid the solver actually ended on.

Run `replay.sh` yourself and leave its output in the submission. The evaluator
also re-runs `replay.sh` from a clean copy and takes both files from *its* own
run, so nothing is gained by hand-editing either of them.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **900 seconds**; a run that overruns is scored zero however good the physics. How much refinement you can afford is therefore part of the problem.

## Analytical-shortcut notice

There is no closed form for a laminar burning velocity — it depends on the full
kinetic mechanism, the transport model and the flame structure, so it can only
come from a solve. Nor is there one for the answer to the requirement above:
where a solution of *this* mixture stops moving under refinement is a property
of this mixture that has to be measured, and a recalled number cannot supply
the table that demonstrates it.
