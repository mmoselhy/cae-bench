# Task -- lid-driven square cavity at Re = 1000

Set up and solve, reproducibly, steady, incompressible, laminar flow in the
classic two-dimensional lid-driven square cavity.

## Engineering specification

- Unit square: `0 <= x <= 1`, `0 <= y <= 1`. The flow is two-dimensional: if
  your tool needs a three-dimensional domain, use a single cell through the
  thickness with no flow or gradients in the spanwise direction.
- Lid speed `U_lid = 1` in the positive x direction and kinematic viscosity
  `nu = 0.001`, so `Re = U_lid L / nu = 1000`.
- The top wall is a moving no-slip wall. The left, right and bottom walls are
  stationary no-slip walls.
- Laminar flow (no turbulence model); steady incompressible solution.
- Resolve the recirculating flow well enough to reproduce the established
  vertical-centerline velocity profile. The scored outcome is the minimum
  `Ux/U_lid` on `x = 0.5`, including the negative back-flow trough.

## Result to report

`results.csv` in the submission root, with a header row and one data row:

| column | meaning |
|---|---|
| `u_min_vertical_centerline` | the minimum `Ux/U_lid` on the vertical centreline `x = 0.5` |

The format, with a placeholder that is not the answer:

```
u_min_vertical_centerline
-0.9
```

How you mesh the cavity, discretise, converge and sample the centreline is
yours to decide -- including the spanwise thickness of a 3-D slab, if you use
one, which is why sampling it is your job and not the evaluator's.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy under a hard limit of
**600 seconds**; a run that overruns is scored zero however good the physics.
