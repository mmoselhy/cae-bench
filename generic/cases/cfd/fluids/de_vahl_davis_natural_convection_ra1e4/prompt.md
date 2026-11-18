# Task -- natural convection cavity at Ra = 10^4

Set up and solve, reproducibly, the de Vahl Davis differentially heated
square-cavity benchmark.

## Engineering specification

- Unit square in x-y. The flow is two-dimensional: if your tool needs a
  three-dimensional domain, use a single cell through the thickness with no
  flow or gradients in the spanwise direction.
- Boussinesq, steady, laminar natural convection; `Ra=1e4`, `Pr=0.71`.
- Use the nondimensional setup `L=1`, `T_hot=1`, `T_cold=0`, `|g|=1`,
  `beta=1`, so `nu=sqrt(0.71e-4)=8.4261498e-3` and `alpha=nu/Pr`.
- Gravity acts in negative y. The left vertical wall is hot, the right wall is
  cold, and horizontal walls are adiabatic. All physical walls are no-slip.
- Resolve the circulation and wall thermal boundary layers sufficiently to
  reproduce the established mean hot-wall Nusselt number.

## Result to report

`results.csv` in the submission root, with a header row and one data row:

| column | meaning |
|---|---|
| `nu_avg_hot_wall` | average Nusselt number on the hot wall, normalised by that wall's own area |

The format, with a placeholder that is not the answer:

```
nu_avg_hot_wall
1.0
```

How you mesh, discretise, converge and extract is yours to decide.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy under a hard limit of
**600 seconds**; a run that overruns is scored zero however good the physics.
