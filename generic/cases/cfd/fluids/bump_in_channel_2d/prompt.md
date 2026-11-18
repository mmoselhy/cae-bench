# Task -- NASA 2D bump-in-channel, turbulent drag

Compute the drag on a smooth bump in a channel and report its coefficient.

## The mesh is supplied

A grid is already in your working directory (under `/tmp/agent/`); its file
format is described in the environment section below. It is NASA's own grid
for this case (14,080 cells, wall-resolved). **Use it as it is** -- do not
regenerate, refine or coarsen it. The expected answer corresponds to this mesh.

## Geometry

Flat plate along the lower boundary over `0 ≤ x ≤ 1.5`, carrying a smooth bump

```
z(x) = 0.05 · sin⁴( πx/0.9 − π/3 )        for 0.3 ≤ x ≤ 1.2
z(x) = 0                                   elsewhere on the plate
```

Upstream of `x = 0` and downstream of `x = 1.5` the lower boundary is a slip
(symmetry) surface, so the boundary layer starts at the plate leading edge. The
domain runs from `x = −25` to `x = 26.5`, with a symmetry ceiling at `z = 5`.
The mesh is one cell deep; the flow is two-dimensional, with no flow or
gradients normal to the two spanwise planes.

Patches, as named in the supplied mesh: `inlet`, `outlet`, `top`, `wall`
(the no-slip plate), `symLower`, `frontBack` (the two spanwise planes).

## Flow conditions

| quantity | value |
|---|---|
| free-stream velocity | 1 (non-dimensional) |
| reference length | 1 |
| Reynolds number | 3 × 10⁶ |
| kinematic viscosity | 3.3333333 × 10⁻⁷ |
| turbulence model | **k-omega SST** (Menter shear-stress-transport two-equation RANS model) |
| free-stream turbulence intensity | 0.077 % |
| free-stream eddy-viscosity ratio | 0.009 |

Treat the flow as incompressible and steady.

The turbulence model is part of the specification, not a choice -- a different
closure gives a different answer.

## Result to report

`results.csv` in the submission root, with a header row and one data row:

| column | meaning |
|---|---|
| `cd_total` | total drag coefficient on the bump |

The format, with a placeholder that is not the answer:

```
cd_total
1.0
```

How you drive the solver is your business.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy under a hard limit of
**2400 seconds**; a run that overruns is scored zero however good the physics.
