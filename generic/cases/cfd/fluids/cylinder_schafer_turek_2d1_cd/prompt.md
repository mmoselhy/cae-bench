# Task -- DFG cylinder benchmark 2D-1

Set up and solve, reproducibly, the steady laminar Schäfer–Turek DFG benchmark
2D-1 and obtain the cylinder drag coefficient.

## Engineering specification

- Channel: `2.2 m` long and `0.41 m` high.
- Cylinder: diameter `D=0.1 m`, centre `(0.2, 0.2)`; retain the specified
  0.005 m offset from the channel centreline.
- The flow is two-dimensional: if your tool needs a three-dimensional domain,
  use a single cell through the thickness with no flow or gradients in the
  spanwise direction.
- `rho=1`, `nu=1e-3 m^2/s`, steady incompressible laminar flow (no turbulence
  model).
- At the inlet use the DFG parabolic profile
  `u(y)=4 Umax y(H-y)/H^2`, with `Umax=0.3 m/s`, `H=0.41 m`; its mean is
  `Umean=0.2 m/s`, giving `Re=20` based on `D`.
- Outlet: zero-gradient velocity and fixed kinematic pressure. Channel walls
  and cylinder: stationary no-slip.
- Resolve the circular surface, wake and wall interaction sufficiently to
  reproduce the established steady cylinder drag.
- Report the drag coefficient `cd`, normalised as the DFG benchmark defines it:
  `cd = 2 F_D / (rho * Umean^2 * D * span)`, with `Umean = 0.2`, `rho = 1`,
  `D = 0.1` and `span` the spanwise thickness of your own model (per unit
  span for a strictly 2-D solver). The spanwise thickness is yours to choose --
  it is a 2D problem -- so the reference area that goes with it is yours to
  get right.

## Result to report

`results.csv` in the submission root, with a header row and one data row:

| column | meaning |
|---|---|
| `cd` | the drag coefficient defined above |

The format, with a placeholder that is not the answer:

```
cd
1.0
```

How you mesh the cylinder, name your boundaries, discretise and extract the
force is yours to decide.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy under a hard limit of
**1800 seconds**; a run that overruns is scored zero however good the physics.
