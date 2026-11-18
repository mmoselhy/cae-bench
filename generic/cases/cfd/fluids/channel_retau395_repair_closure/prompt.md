# Task -- a channel-flow case that returns the wrong bulk velocity

*Native-only task: the case to repair is supplied in one tool's own input
format (described in the environment section), and the repair has to be made
in that case.*

An engineer set up the simulation case in `case/` (in your working directory,
under `/tmp/agent/`) for fully-developed plane channel flow and handed it over.
It meshes and it runs to completion -- and the bulk velocity it reports is far
too high for the Reynolds number the case is supposed to be at, by close to an
order of magnitude.

Find out why, fix it, and hand back a case that produces the right answer.

## What the case is meant to represent

- Channel half-height `delta = 1`, full height `2`; periodic streamwise length
  `4`; two-dimensional, represented by a single cell through the thickness with
  no flow or gradients in the spanwise direction.
- No-slip walls on both sides, periodic (cyclic) streamwise boundaries.
- `u_tau = 1`, `nu = 1/395`, and a uniform streamwise body force of magnitude
  `u_tau^2 / delta = 1`. By momentum balance that forcing fixes the friction
  Reynolds number at `Re_tau = 395` -- the flow is **fully turbulent**, not a
  laminar Poiseuille flow.
- Because the forcing fixes `u_tau`, the bulk velocity is an *output* of the
  solve. `U_b / u_tau = U_b` is the quantity that is checked.

The geometry, the mesh, the boundary conditions, the material properties and
the body force are all consistent with that specification. The defect is
somewhere else, and it is a single modelling decision rather than a typo.

## What to change

Whatever is required to make the case represent the physics above. If your fix
introduces fields or settings the current case does not carry, add them -- a
correct case is the deliverable, not a minimal diff. Keep `Re_tau = 395`:
do not change `nu`, the body force, the geometry or the mesh to move the
answer, because those are what define the operating point.

**The iteration budget is part of the problem, not part of the defect.** The
supplied case runs a fixed number of iterations and stops there, and every
submission is solved under that same budget so that the answers are comparable.
Leave it as it is. Running longer is not the fix -- the defect is a single
modelling decision, and the answer this task checks is the one that budget
produces.

## Result to report

`results.csv` in the submission root, with a header row and one data row:

| column | meaning |
|---|---|
| `ub_over_utau` | bulk velocity divided by the friction velocity |

The format, with a placeholder that is not the answer:

```
ub_over_utau
1.0
```

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy under a hard limit of
**600 seconds**; a run that overruns is scored zero however good the physics.
