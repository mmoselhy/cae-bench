- `case/` is a native OpenFOAM case: `0/`, `constant/` and `system/`, a
  `system/blockMeshDict` mesh, an `Allrun` that drives `blockMesh`, a steady
  incompressible solver and the bulk-velocity post-processing, and
  `extract_channel.py`. The spanwise faces are `empty`; the streamwise
  boundaries are `cyclic`; the body force is a `vectorSemiImplicitSource` in
  `constant/fvOptions`.
- The repaired case goes in the submission (its `0/`, `constant/` and `system/`
  at the submission root); `replay.sh` may call the case's own `Allrun` or do
  the same steps. Leave the iteration budget (`endTime` in `system/controlDict`)
  as it is.
