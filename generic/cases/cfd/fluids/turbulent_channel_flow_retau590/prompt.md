# Task -- fully-developed turbulent plane-channel flow at Re_tau = 590

Set up, reproducibly, steady, fully-developed turbulent flow in a smooth plane
channel. You may run and revise the case as needed before submitting it.

## Geometry

- A plane channel between two parallel flat walls, half-height δ (the full
  channel height is 2δ). Use the box `0 ≤ x ≤ 4`, `−1 ≤ y ≤ 1`, and
  `0 ≤ z ≤ 1`, so δ = 1 (non-dimensional).
- The streamwise direction (x) is **statistically homogeneous**: the flow is
  fully developed, with no streamwise variation of the mean profile. Model x as
  **periodic** over a short box (a length of a few δ is sufficient).
- The mean flow is one-dimensional (depends only on the wall-normal coordinate
  y). Treat the spanwise direction with a single cell (2D, or no flow or
  gradients across the span, or periodic -- whatever your solver requires).

## Flow conditions

- Friction Reynolds number **Re_τ = u_τ · δ / ν = 590**, where
  u_τ = √(τ_w / ρ) is the friction velocity and τ_w the mean wall shear stress.
- Incompressible, Newtonian, constant properties.
- The flow is **fully turbulent** and must be computed with the k-omega SST
  RANS model (Menter shear-stress-transport two-equation model). Use a
  low-Reynolds, wall-resolved mesh with first-cell y⁺ ≤ 1.

## Driving the flow

A fully-developed channel has no net pressure difference across a periodic box;
it is driven by a **uniform streamwise forcing** that balances the wall
friction. The global x-momentum balance over the full channel height is

    (driving force per unit volume) · (2δ)  =  2 · τ_w,

so a uniform body force of magnitude `g = u_τ² / δ` makes the friction velocity
exactly `u_τ = √(g·δ)`. A convenient, fully-specified choice is

- **u_τ = 1** and **δ = 1**, hence a uniform streamwise body force `g = 1`, and
- **ν = u_τ · δ / Re_τ = 1 / 590 = 0.00169492** (kinematic viscosity).

Apply the forcing as a uniform, explicit streamwise momentum source of `1`
(per unit mass, i.e. an acceleration `(1, 0, 0)`) over the whole domain.

With this choice the friction velocity is known a priori (u_τ = 1), so you do
not need to post-process the wall shear to get it — but your mesh and model
must still reproduce the correct turbulent mean profile.

## Boundary conditions

- Walls (y = ±δ): no-slip, smooth, with the turbulence wall treatment your
  model requires.
- Streamwise faces (x): periodic / cyclic.
- Spanwise faces: 2D / no flow or gradients across the span / periodic.

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

How you mesh, discretise, converge and extract is yours to decide.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy under a hard limit of
**600 seconds**; a run that overruns is scored zero however good the physics.
