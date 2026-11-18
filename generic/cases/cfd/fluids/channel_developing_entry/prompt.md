# Task -- developing laminar channel entry at Re = 100

Set up and solve, reproducibly, the entrance region of a two-dimensional plane
channel.

## Engineering specification

- Full channel height `D=2H=1`, walls at `y=+-0.5`, length `6`.
- The flow is two-dimensional: if your tool needs a three-dimensional domain,
  use a single cell through the thickness with no flow or gradients in the
  spanwise direction.
- Uniform inlet velocity `Umean=1`, `nu=0.01`, giving `Re=Umean D/nu=100`.
- Steady incompressible laminar flow (no turbulence model); stationary no-slip
  channel walls; fixed-pressure outlet with zero-gradient velocity.
- Resolve the developing entrance flow sufficiently to reproduce the
  centreline velocity ratio `Ux/Umean` at `x=0.01 Re D=1`. This is the scored
  field outcome; the flow is not yet fully developed there.

## Result to report

`results.csv` in the submission root, with a header row and one data row:

| column | meaning |
|---|---|
| `u_centerline_ratio` | centreline velocity at x = 1 divided by the inlet mean velocity |

The format, with a placeholder that is not the answer:

```
u_centerline_ratio
1.0
```

How you mesh, discretise, converge and extract is yours to decide.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy under a hard limit of
**600 seconds**; a run that overruns is scored zero however good the physics.
