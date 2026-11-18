- The supplied grid is an OpenFOAM mesh at `constant/polyMesh/` (gzip-compressed
  files, which OpenFOAM reads as they are), and it is the only thing in your
  working directory. Solve on it as it is. `frontBack` is an `empty` patch.
- Spalart-Allmaras is OpenFOAM's `SpalartAllmaras` RAS model.
