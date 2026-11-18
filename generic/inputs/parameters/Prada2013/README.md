# Cell parameter data sheet (`cell.json`)

Tool-neutral parameter values for this task's cell. Format
`caebench-tn-cell-datasheet-v1`, JSON:

* `scalars` -- `{"<quantity [unit]>": value}`, SI units as spelled in the name.
* `functions` -- quantities that depend on state. Each has `args` (the varying
  arguments, e.g. `sto` = particle stoichiometry, `c_e` = electrolyte
  concentration [mol.m-3], `c_s_surf` = particle-surface concentration [mol.m-3],
  `T` = temperature [K]), one `grid` per argument, and `values` laid out so that
  `values[i][j]...` is the quantity at `(grid[0][i], grid[1][j], ...)`. `fixed`
  lists constants of the cell the function also depends on (e.g. `c_s_max`).
  Interpolate linearly; extrapolate linearly outside the grid.
* `other` -- non-numeric entries, verbatim.

47 scalars and 5 tabulated functions. Generated from a published
parameter set (Prada2013) as distributed with PyBaMM 26.7.1.0; the names follow
PyBaMM's spelling, which states each unit in brackets.
