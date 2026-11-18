- Use the RAS model `kOmegaSST`, `cyclic` streamwise patches and `empty` (or
  `cyclic`) spanwise faces.
- Implement the forcing with an OpenFOAM `vectorSemiImplicitSource` in either
  `constant/fvOptions` or `system/fvOptions`, using `selectionMode all`,
  `volumeMode specific`, and the velocity source `U ((1 0 0) 0)`.
