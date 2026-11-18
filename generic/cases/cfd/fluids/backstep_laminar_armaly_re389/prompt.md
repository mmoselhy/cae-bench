# Task -- laminar backward-facing step at Re = 389

Set up and solve, reproducibly, the Armaly et al. laminar backward-facing-step
validation condition and obtain the primary reattachment length.

## Engineering specification

- Step height `S=0.0049 m`; expansion ratio `H_out/H_in=1.94`.
- Use the supplied physical scale with upstream development length at least
  `20S` and downstream length at least `30S`.
- Mean inlet speed `Umean=1 m/s`, `nu=2.51928e-5 m^2/s`, giving
  `Re=Umean(2S)/nu=389`.
- Steady incompressible laminar flow (no turbulence model). The flow is
  two-dimensional: if your tool needs a three-dimensional domain, use a single
  cell through the thickness with no flow or gradients in the spanwise
  direction.
- Inlet velocity is uniform and the upstream section develops it before the
  step. Outlet uses fixed kinematic pressure / zero-gradient velocity. All
  physical walls and the step face are stationary no-slip.
- Resolve the separated shear layer and downstream wall shear sufficiently to
  locate the first negative-to-positive wall-shear crossing after the step.
  The scored outcome is `x_r/S`.

## Result to report

`results.csv` in the submission root, with a header row and one data row:

| column | meaning |
|---|---|
| `reattachment_length_xr_over_h` | reattachment length on the downstream floor, in step heights |

The format, with a placeholder that is not the answer:

```
reattachment_length_xr_over_h
1.0
```

How you mesh, discretise, converge and extract is yours to decide.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy under a hard limit of
**2400 seconds**; a run that overruns is scored zero however good the physics.
