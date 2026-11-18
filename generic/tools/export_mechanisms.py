"""Export every mechanism the combustion track names to Chemkin format.

Run inside sim-benchmark-combustion-fullstack (Cantera 3.2.0):
    python3 export_mechanisms.py <out_dir>
Writes <out_dir>/<id>/{chem.inp,therm.dat,tran.dat,SOURCE.json}. The native
YAML is not copied: it ships with Cantera and the opensource profile loads it
by name, exactly as upstream.
"""
import json, sys
from pathlib import Path
import cantera as ct

MECHS = {
    "gri30": ("gri30.yaml", None),
    "h2o2": ("h2o2.yaml", None),
    "ndodecane_reitz": ("nDodecane_Reitz.yaml", "nDodecane_IG"),
    "nh3_co_h2_alzueta2023": ("example_data/ammonia-CO-H2-Alzueta-2023.yaml", None),
    "nhexane_nuig2015": ("example_data/n-hexane-NUIG-2015.yaml", None),
}
out = Path(sys.argv[1])
for mid, (src, phase) in MECHS.items():
    d = out / mid
    d.mkdir(parents=True, exist_ok=True)
    gas = ct.Solution(src, phase) if phase else ct.Solution(src)
    has_tran = gas.transport_model not in ("none", None, "")
    gas.write_chemkin(d / "chem.inp", thermo_path=d / "therm.dat",
                      transport_path=(d / "tran.dat") if has_tran else None,
                      overwrite=True, quiet=True)
    (d / "SOURCE.json").write_text(json.dumps({
        "exported_from": src, "phase": phase, "cantera_version": ct.__version__,
        "n_species": gas.n_species, "n_reactions": gas.n_reactions,
        "transport": gas.transport_model if has_tran else None,
        "method": "cantera.Solution.write_chemkin",
    }, indent=2))
    print(mid, gas.n_species, gas.n_reactions, gas.transport_model)
