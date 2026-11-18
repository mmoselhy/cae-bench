"""Tool-neutral battery parameter data sheet: export from PyBaMM, load back.

    python3 cell_datasheet.py export <PyBaMM set> <out_dir>    # writes cell.json + README.md
    python3 cell_datasheet.py check  <PyBaMM set> <cell.json>  # max table error vs. the native functions

Format `caebench-tn-cell-datasheet-v1` (JSON):
  scalars    {"<name [unit]>": number}
  functions  {"<name [unit]>": {"args": [...], "grid": [[...], ...], "values": nested list,
                                "fixed": {"<arg>": number}}}
             -- `values[i][j]...` is the function at (grid[0][i], grid[1][j], ...); arguments
                in `fixed` are constants of the cell the native function takes as inputs
                (e.g. the electrode's maximum concentration) and are not tabulated.
  other      non-numeric entries, verbatim
Parameter names are PyBaMM's (they spell the unit in brackets) because they are
the most widely reused naming for these quantities; nothing else in the file is
PyBaMM-specific. Run inside sim-benchmark-battery-fullstack.
"""
from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import numpy as np
import pybamm

FORMAT = "caebench-tn-cell-datasheet-v1"


def _grid(arg: str, key: str, pv) -> np.ndarray | None:
    """Tabulation grid for one argument, or None if it is a cell constant."""
    if arg == "sto":
        edge = np.array([1e-6, 1e-5, 1e-4, 5e-4, 1e-3, 2e-3, 5e-3])
        return np.unique(np.concatenate([edge, np.linspace(0.01, 0.99, 491), 1 - edge]))
    if arg in ("T", "T_dim"):
        return np.linspace(233.15, 373.15, 15)
    if arg == "c_e":
        c0 = float(pv.get("Initial concentration in electrolyte [mol.m-3]", 1000.0))
        return np.linspace(1.0, max(4.0 * c0, 4000.0), 41)
    if arg == "c_s_surf":
        return np.linspace(0.0, _c_s_max(key, pv), 51)
    if arg == "c_Li":
        return np.concatenate([[0.0], np.geomspace(1e-3, 1e5, 40)])
    if arg == "L_sei":
        return np.geomspace(1e-12, 1e-5, 41)
    return None


def _c_s_max(key: str, pv) -> float:
    side = "negative" if key.lower().startswith("negative") else "positive"
    return float(pv[f"Maximum concentration in {side} electrode [mol.m-3]"])


def _fixed(arg: str, key: str, pv) -> float:
    if arg == "c_s_max":
        return _c_s_max(key, pv)
    if arg == "T_ref":
        return float(pv["Reference temperature [K]"])
    if arg == "t_plus":
        return float(pv["Cation transference number"])
    raise KeyError(f"{key}: no rule for argument {arg!r}")


def _evaluate(fn, args, grids, fixed, pv) -> np.ndarray:
    mesh = np.meshgrid(*grids, indexing="ij")
    flat = [m.reshape(-1, 1) for m in mesh]
    it = iter(flat)
    call = [pybamm.Scalar(fixed[a]) if a in fixed else pybamm.Vector(next(it)) for a in args]
    out = fn(*call)
    val = pv.process_symbol(out).evaluate() if isinstance(out, pybamm.Symbol) else out
    val = np.asarray(val, dtype=float).reshape(-1)
    if val.size == 1:
        val = np.full(flat[0].shape[0], float(val[0]))
    return val.reshape(mesh[0].shape)


def export(name: str) -> dict:
    pv = pybamm.ParameterValues(name)
    scalars, functions, other = {}, {}, {}
    for key, v in sorted(pv.items()):
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            scalars[key] = float(v)
        elif callable(v):
            args = list(inspect.signature(v).parameters)
            fixed = {a: _fixed(a, key, pv) for a in args if _grid(a, key, pv) is None}
            grids = [_grid(a, key, pv) for a in args if a not in fixed]
            vals = _evaluate(v, args, grids, fixed, pv)
            if not np.all(np.isfinite(vals)):
                raise ValueError(f"{name}: {key} is not finite on its grid")
            functions[key] = {"args": [a for a in args if a not in fixed], "fixed": fixed,
                              "native_args": args,
                              "grid": [g.tolist() for g in grids], "values": vals.tolist()}
        else:
            try:
                json.dumps(v)
                other[key] = v
            except TypeError:
                other[key] = repr(v)
    return {"format": FORMAT,
            "source": {"pybamm_parameter_set": name, "pybamm_version": pybamm.__version__,
                       "method": "scalars copied; functions evaluated on the grids given"},
            "scalars": scalars, "functions": functions, "other": other}


def load(path: str | Path) -> pybamm.ParameterValues:
    """Build PyBaMM parameter values from a data sheet (the round-trip half)."""
    sheet = json.loads(Path(path).read_text())
    assert sheet["format"] == FORMAT
    values: dict = dict(sheet["scalars"])
    values.update({k: v for k, v in sheet["other"].items() if not isinstance(v, str)})
    for key, f in sheet["functions"].items():
        values[key] = _interp_fn(key, f)
    return pybamm.ParameterValues(values)


def _interp_fn(key: str, f: dict):
    grids = [np.asarray(g, dtype=float) for g in f["grid"]]
    data = np.asarray(f["values"], dtype=float)
    tab = set(f["args"])

    def fn(*call):
        # The model calls with the native argument list; keep the tabulated ones.
        children = [c for c, n in zip(call, f["native_args"]) if n in tab]
        x = grids[0] if len(grids) == 1 else grids
        return pybamm.Interpolant(x, data, children if len(children) > 1 else children[0],
                                  name=key, interpolator="linear", extrapolate=True)
    return fn


def main() -> int:
    cmd, name = sys.argv[1], sys.argv[2]
    if cmd == "export":
        out = Path(sys.argv[3])
        out.mkdir(parents=True, exist_ok=True)
        sheet = export(name)
        (out / "cell.json").write_text(json.dumps(sheet, separators=(",", ":")))
        (out / "README.md").write_text(README.format(name=name, version=pybamm.__version__,
                                                     n_s=len(sheet["scalars"]), n_f=len(sheet["functions"])))
        print(name, len(sheet["scalars"]), "scalars", len(sheet["functions"]), "functions",
              f"{(out / 'cell.json').stat().st_size / 1e6:.2f} MB")
    return 0


README = """# Cell parameter data sheet (`cell.json`)

Tool-neutral parameter values for this task's cell. Format
`caebench-tn-cell-datasheet-v1`, JSON:

* `scalars` -- `{{"<quantity [unit]>": value}}`, SI units as spelled in the name.
* `functions` -- quantities that depend on state. Each has `args` (the varying
  arguments, e.g. `sto` = particle stoichiometry, `c_e` = electrolyte
  concentration [mol.m-3], `c_s_surf` = particle-surface concentration [mol.m-3],
  `T` = temperature [K]), one `grid` per argument, and `values` laid out so that
  `values[i][j]...` is the quantity at `(grid[0][i], grid[1][j], ...)`. `fixed`
  lists constants of the cell the function also depends on (e.g. `c_s_max`).
  Interpolate linearly; extrapolate linearly outside the grid.
* `other` -- non-numeric entries, verbatim.

{n_s} scalars and {n_f} tabulated functions. Generated from a published
parameter set ({name}) as distributed with PyBaMM {version}; the names follow
PyBaMM's spelling, which states each unit in brackets.
"""

if __name__ == "__main__":
    raise SystemExit(main())
