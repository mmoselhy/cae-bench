- The supplied grid is an OpenFOAM mesh at `constant/polyMesh/` (gzip-compressed
  files, which OpenFOAM reads as they are). Use it as it is: do not run
  `blockMesh` or any other mesher over it. `frontBack` is an `empty` patch.
- The k-omega SST model is OpenFOAM's `kOmegaSST`, used with a steady
  incompressible OpenFOAM solver.
