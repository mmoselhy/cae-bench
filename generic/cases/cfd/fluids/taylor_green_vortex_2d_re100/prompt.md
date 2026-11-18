# Task -- 2D Taylor–Green vortex decay at Re = 100

Set up and solve, reproducibly, the transient flow of the exact
two-dimensional Taylor–Green vortex.

## Engineering specification

- Doubly periodic box `0 <= x,y <= 2 pi`. The flow is two-dimensional: if your
  tool needs a three-dimensional domain, use a single cell through the
  thickness with no flow or gradients in the spanwise direction.
- `nu=0.01` (`Re=100` for unit length/velocity); incompressible laminar flow
  (no turbulence model).
- At `t=0` impose
  `Ux=-cos(x) sin(y)`, `Uy=sin(x) cos(y)`, `Uz=0` and a compatible pressure
  gauge.
- Integrate the transient Navier–Stokes equations to `t*=5` with adequate
  spatial and temporal resolution. Do not substitute the analytic decay for
  the solver run.
- The scored outcome is the maximum cell-centre `|Ux|` in the final computed
  field; the exact solution decays uniformly as `exp(-2 nu t)`.

## Result to report

`results.csv` in the submission root, with a header row and one data row:

| column | meaning |
|---|---|
| `u_peak_at_tstar` | peak \|Ux\| in the final velocity field |

The format, with a placeholder that is not the answer:

```
u_peak_at_tstar
1.0
```

How you mesh, discretise, converge and extract is yours to decide.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy under a hard limit of
**600 seconds**; a run that overruns is scored zero however good the physics.
