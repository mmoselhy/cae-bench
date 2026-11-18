#!/usr/bin/env bash
# Round-trip leg of the mesh proof: Gmsh MSH -> OpenFOAM polyMesh via gmshToFoam,
# patch types restored from <mesh>.patches.json. Run in sim-benchmark-cfd-fullstack.
#   gmsh_to_polymesh.sh <mesh.msh> <out_case_dir>
set -eo pipefail
MSH="$1"; OUT="$2"
source /usr/lib/openfoam/openfoam2412/etc/bashrc >/dev/null 2>&1 || true
set -u
mkdir -p "$OUT/system" "$OUT/constant"
cat > "$OUT/system/controlDict" <<'CD'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application simpleFoam; startFrom startTime; startTime 0; stopAt endTime; endTime 1;
deltaT 1; writeControl timeStep; writeInterval 1; writeFormat ascii; writePrecision 17;
CD
gmshToFoam "$MSH" -case "$OUT" > "$OUT/log.gmshToFoam" 2>&1
python3 - "$MSH" "$OUT" <<'PY'
import json, re, sys
from pathlib import Path
meta = json.loads(Path(sys.argv[1]).with_suffix(".patches.json").read_text())
b = Path(sys.argv[2]) / "constant/polyMesh/boundary"
s = b.read_text()
for p in meta["patches"]:
    def fix(m, p=p):
        blk = re.sub(r"type\s+\w+;", f"type {p['type']};", m.group(2))
        blk = re.sub(r"\s*inGroups[^;]*;", "", blk)
        if p.get("inGroups"):
            blk = blk.replace(f"type {p['type']};", f"type {p['type']};\n        inGroups {p['inGroups']};")
        return m.group(1) + blk + "}"
    s, n = re.subn(r"(\b" + re.escape(p["name"]) + r"\s*\{)([^}]*)\}", fix, s)
    assert n == 1, p["name"]
b.write_text(s)
PY
ls "$OUT/constant/polyMesh"
