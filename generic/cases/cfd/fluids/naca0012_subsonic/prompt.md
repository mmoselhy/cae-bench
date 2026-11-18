# Task -- NACA 0012 airfoil, subsonic turbulent, on a supplied grid

Predict the steady aerodynamic loads on a NACA 0012 airfoil in
fully-turbulent subsonic flow at a single angle of attack, and report the
integral force coefficients.

## The mesh is supplied

Your working directory (under `/tmp/agent/`) contains a structured C-grid
around the airfoil, 14 336 cells, wall-resolved (first-layer spacing
8.0 × 10⁻⁶ c, so no wall functions are needed or wanted); its file format is
described in the environment section below. **Solve on this mesh.** It is the
grid the reference solution was computed on; a different mesh answers a
different question, and the cell-count check will show it.

It is also supplied in a tool-neutral form, `/tmp/agent/inputs/mesh/mesh.msh`
(Gmsh MSH 2.2 ASCII: hexahedra in physical group `fluid`, boundary quads in one
physical group per patch, named as below), with the patch types (wall, inflow/outflow,
spanwise) in `mesh.patches.json` beside it. Both forms are the same grid.

Patches, as named in the supplied mesh:

| patch | what it is |
|---|---|
| `aerofoil` | the airfoil surface — no-slip, adiabatic |
| `farfield` | outer boundary and both downstream planes, ≈ 500 c away — characteristic / Riemann-invariant freestream |
| `frontBack` | the two spanwise planes of the one-cell-deep 2D slab — no flow or gradients normal to them |

## Geometry

NACA 0012 section, sharp closed trailing edge, chord c = 1 m, leading edge
at the origin, chord along the x-axis, so the airfoil occupies x/c ∈ [0, 1].

The grid is **not** pre-rotated. Impose the angle of attack through the
freestream direction rather than by rotating the mesh, and rotate the
lift/drag directions to match.

## Flow conditions

| quantity | value |
|---|---|
| angle of attack | α = 10° |
| chord Reynolds number | 6 × 10⁶ |
| free-stream Mach | 0.15 — low enough to treat as incompressible |
| boundary-layer state | fully turbulent (tripped at the leading edge) |
| turbulence model | **Spalart-Allmaras** (one-equation RANS model) |

The turbulence model is part of the specification, not a choice — a different
closure gives a different answer, and the reference this case is scored
against was computed with this one. There is no restriction on numerical
scheme.

Reference quantities for the coefficients: dynamic pressure ½·ρ_∞·U_∞²,
reference area A_ref = c × span = 1, reference length l_ref = c = 1.

## Result to report

`results.csv` in the submission root, with a header row and one data row:

| column | meaning |
|---|---|
| `CL_at_alpha_10` | lift coefficient at 10 degrees incidence |
| `CD_at_alpha_10` | drag coefficient at 10 degrees incidence |

The format, with placeholders that are not the answer:

```
CL_at_alpha_10,CD_at_alpha_10
9.99,9.99
```

## Analytical-shortcut notice

Thin-airfoil theory gives a lift-curve slope of 2π per radian, and that is
**not** enough to satisfy the tolerance here: at finite Reynolds number the
real slope is modified by viscosity, finite thickness and trailing-edge
behaviour, and the band this case scores against is tighter than that
discrepancy. Drag has no closed form at all — its viscous part requires
actually resolving the boundary layer on the supplied grid. A recalled
correlation cannot produce both coefficients.

## Reference

- NASA Turbulence Modeling Resource, NACA 0012 grids and numerics study:
  https://tmbwg.github.io/turbmodels/naca0012numerics_val.html
- Ladson, C. L. (1988). *Effects of Independent Variation of Mach and
  Reynolds Numbers on the Low-Speed Aerodynamic Characteristics of the
  NACA 0012 Airfoil Section*. NASA TM-4074.

## Time budget

The evaluator re-runs your `replay.sh` from a clean copy under a hard limit of
**900 seconds**; a run that overruns is scored zero however good the physics.
