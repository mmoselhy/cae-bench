"""Prove a neutral-input conversion by solving the oracle from the neutral input.

    python3 prove_conversions.py battery    <repo> <out.json>   # in the battery image
    python3 prove_conversions.py combustion <repo> <out.json>   # in the combustion image

For every task of the domain: run the UNCHANGED upstream oracle `run_case.py`
twice in scratch directories -- once as shipped (native input), once with only
the input-loading call redirected to the neutral file -- derive the KPIs from
each run's own results.csv with the upstream extractor, and record both values,
their difference, and whether the neutral-input value is still inside the band.

battery:    `pybamm.ParameterValues(PARAMETER_SET)` -> `cell_datasheet.load(<cell.json>)`
combustion: the mechanism string -> a YAML made by Cantera's `ck2yaml` from the
            exported Chemkin files (Chemkin -> YAML: the direction a tool that only
            reads Chemkin depends on).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DOMAIN, REPO, OUT = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
GEN = REPO / "generic"
sys.path.insert(0, str(GEN / "tools"))
sys.path.insert(0, str(REPO / "lib" / "sim_benchmark_verifier"))


def extract(case: Path, workdir: Path) -> dict:
    spec = json.loads((case / "tests" / "spec.json").read_text())
    if DOMAIN == "battery":
        from sim_benchmark_verifier import native_pybamm as m
        s = m.PyBaMMSpec(**spec)
        out = m.EXTRACTORS[s.kind](m.read_results_csv(workdir / "results.csv"), s)
    else:
        from sim_benchmark_verifier import native_cantera as m
        s = m.CanteraSpec(**{k: v for k, v in spec.items() if k not in m._RETIRED_SPEC_KEYS})
        aux = m.read_results_csv(workdir / s.second_profile) if s.second_profile else None
        out = m.with_declared(m.EXTRACTORS[s.kind], s)(m.read_results_csv(workdir / "results.csv"), s, aux)
    kp = json.loads((case / "tests" / "kpis.json").read_text())["kpis"]
    return {k: float(out[k]) for k in kp if k in out}


def run(case: Path, patch) -> tuple[dict, float, str]:
    with tempfile.TemporaryDirectory() as tmp:
        w = Path(tmp)
        src = (case / "solution" / "run_case.py").read_text()
        env_dir = case / "environment"
        for p in env_dir.rglob("*"):  # task-supplied fixtures, as the agent would see them
            if p.is_file() and p.name not in ("README.md", ".case"):
                d = w / p.relative_to(env_dir)
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, d)
        if patch is not None:
            src = patch(src, w)
        (w / "run_case.py").write_text(src)
        t0 = time.time()
        r = subprocess.run([sys.executable, "run_case.py"], cwd=w, capture_output=True, text=True)
        if r.returncode != 0:
            return {}, time.time() - t0, (r.stderr or r.stdout)[-400:]
        return extract(case, w), time.time() - t0, ""


def battery_patch(case: Path):
    ps = json.loads((case / "tests" / "spec.json").read_text())["parameter_set"]
    sheet = GEN / "inputs" / "parameters" / ps / "cell.json"

    def patch(src: str, w: Path) -> str:
        n = src.count("pybamm.ParameterValues(PARAMETER_SET)")
        if n == 0:
            raise RuntimeError("no ParameterValues(PARAMETER_SET) call to redirect")
        return ("import sys as _tn_sys; _tn_sys.path.insert(0, %r)\nimport cell_datasheet as _tn_cell\n" % str(GEN / "tools")
                + src.replace("pybamm.ParameterValues(PARAMETER_SET)", "_tn_cell.load(%r)" % str(sheet)))
    return patch


MECH_ID = {"gri30.yaml": "gri30", "h2o2.yaml": "h2o2", "nDodecane_Reitz.yaml": "ndodecane_reitz",
           "example_data/ammonia-CO-H2-Alzueta-2023.yaml": "nh3_co_h2_alzueta2023",
           "example_data/n-hexane-NUIG-2015.yaml": "nhexane_nuig2015"}


def combustion_patch(case: Path):
    spec = json.loads((case / "tests" / "spec.json").read_text())
    mech, phase = spec["mechanism"], spec.get("phase")
    d = GEN / "inputs" / "mechanisms" / MECH_ID[mech]

    def patch(src: str, w: Path) -> str:
        out = w / "neutral_mech.yaml"
        cmd = [sys.executable, "-m", "cantera.ck2yaml", f"--input={d / 'chem.inp'}",
               f"--thermo={d / 'therm.dat'}", f"--output={out}", "--quiet", "--permissive"]
        if (d / "tran.dat").is_file():
            cmd.append(f"--transport={d / 'tran.dat'}")
        if phase:
            cmd.append(f"--name={phase}")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        # Redirect every quoted occurrence of the native mechanism name.
        new, n = re.subn(r"([\"'])" + re.escape(mech) + r"\1", repr(str(out)), src)
        if n == 0:
            raise RuntimeError(f"mechanism string {mech!r} not found in run_case.py")
        return new
    return patch


def main() -> int:
    cases = sorted(p.parent for p in (REPO / "cases" / DOMAIN).rglob("task.toml"))
    report = {}
    for case in cases:
        key = str(case.relative_to(REPO / "cases"))
        kp = json.loads((case / "tests" / "kpis.json").read_text())["kpis"]
        try:
            native, tn_, err_n = run(case, None)
            neutral, tn2, err_t = run(case, battery_patch(case) if DOMAIN == "battery" else combustion_patch(case))
        except Exception as exc:  # noqa: BLE001
            report[key] = {"error": f"{type(exc).__name__}: {exc}"}
            print(key, "ERROR", exc, flush=True)
            continue
        rows = {}
        for k, spec in kp.items():
            a, b = native.get(k), neutral.get(k)
            row = {"native": a, "neutral": b}
            if a is not None and b is not None:
                tol = float(spec["pass_tol"])
                row.update({"abs_diff": abs(a - b), "rel_diff": abs(a - b) / max(abs(a), 1e-300),
                            "diff_in_band_widths": abs(a - b) / tol,
                            "neutral_inside_band": abs(b - float(spec["gt_value"])) <= tol})
            rows[k] = row
        report[key] = {"kpis": rows, "wall_native_s": round(tn_, 1), "wall_neutral_s": round(tn2, 1),
                       **({"native_error": err_n} if err_n else {}), **({"neutral_error": err_t} if err_t else {})}
        print(key, json.dumps(rows), flush=True)
        OUT.write_text(json.dumps(report, indent=2))
    OUT.write_text(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
