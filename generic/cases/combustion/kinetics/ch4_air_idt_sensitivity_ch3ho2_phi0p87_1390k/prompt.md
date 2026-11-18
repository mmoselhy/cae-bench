# How strongly one reaction controls the ignition delay of lean methane/air

A mechanism has hundreds of rate constants and most of them barely matter.
Which ones do, and by how much, is what decides where measurement effort goes
when a mechanism is being refined. Quantify it for one reaction at one
operating point.

## Mixture and operating point

| quantity | value |
|---|---|
| fuel | methane |
| oxidizer | air, `O2:1, N2:3.76` |
| equivalence ratio | 0.87 |
| initial temperature | 1390 K |
| initial pressure | 2.4 atm |
| mechanism | GRI-Mech 3.0 (53 species, 325 reactions); supplied in Chemkin format under `/tmp/agent/inputs/mechanism/` (`chem.inp`, `therm.dat`) |

Ignite the mixture as a **constant-volume adiabatic** reactor — a closed,
fixed-volume, homogeneous batch of gas with no heat loss.

## What ignition delay means here

The **ignition delay** is the time at which the rate of temperature rise
`dT/dt` reaches its maximum. Integrate past ignition until `dT/dt` has fallen
below 0.1% of the maximum value it reached, so the trace brackets the maximum
rather than ending on it.

## The sensitivity asked for

For the single reaction

> **`CH3 + HO2 <=> CH3O + OH`**

report the **logarithmic sensitivity of the ignition delay to that reaction's
rate constant**:

```
S  =  d ln(tau)  /  d ln(k)
```

where `tau` is the ignition delay above and `k` is the rate constant of that
one reaction, with every other reaction left alone.

Two things about this definition are load-bearing, and both are stated because
the alternatives are in common use and give different numbers:

- **It is the derivative in the limit of a small perturbation**, not the change
  produced by some particular finite one. A "percent sensitivity" defined by
  doubling a rate is a different quantity and is not what is asked for.
- **Your estimate must have converged.** Whatever perturbation you evaluate the
  derivative with, refine it until the estimate has stopped moving to within a
  small fraction of a percent, and report the converged value. Choosing that
  perturbation is part of the problem: too large and the estimate is measuring
  curvature rather than the derivative, too small and it is measuring the
  integrator's own noise.

Report the signed value. (For scale, and as a formatting example only: a value
of `-40` or `+25` would be far outside anything a single elementary reaction
produces here.)

## Output files

Write these into the submission root. `replay.sh` must perform the whole
calculation, **including the perturbation study**.

Note what this means for how the answer is produced: the evaluator strips
every numeric artifact — `results.csv` included — and re-runs `replay.sh`, so
a sensitivity written into the file by hand reproduces nothing. The replay has
to compute it.

- **`results.csv`** — the raw numerical output, written by `replay.sh`, of
   the ignition **at the unperturbed rates**, with a header row and these
   columns:
   - `time_s` — time in seconds, increasing from 0
   - `T_K` — temperature in kelvin
   - `P_Pa` — pressure in pascal
   - `s_ch3_ho2` — the converged sensitivity you are reporting, repeated on
     every row

   Write every column at full numerical precision — do not round the values or
   format them to a fixed number of decimal places — and place the rows closely
   enough together that the ignition delay is resolved by the file itself. The
   delay is read off this file and nothing else, so it can be no sharper than
   the spacing between the rows on either side of the `dT/dt` maximum.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy of the submission under a hard limit of **900 seconds**; a run that overruns is scored zero however good the physics. How many perturbations you can afford is therefore part of the problem.
