"""Convert a hexahedral OpenFOAM polyMesh to a Gmsh MSH 2.2 file.

    python3 polymesh_to_gmsh.py <case_dir_with_constant/polyMesh> <out.msh>

Every cell must be a hexahedron (6 quad faces), which holds for both grids the
cfd track supplies. Boundary faces are written as quads in one physical group
per patch, named after the patch; cells go in physical group "fluid". The
patch *types* (wall / patch / empty) are not part of the MSH format and are
listed in `<out>.patches.json` beside it.

Run inside sim-benchmark-cfd-fullstack (needs NumPy only).
"""
from __future__ import annotations

import gzip
import json
import re
import sys
from pathlib import Path

import numpy as np


def _read(path: Path) -> str:
    gz = path.with_name(path.name + ".gz")
    if path.is_file():
        return path.read_text()
    return gzip.open(gz, "rt").read()


def _body(text: str) -> str:
    """Strip the FoamFile header and comments; return the data part."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    i = text.index("}", text.index("FoamFile"))
    return text[i + 1:]


def _list(text: str) -> tuple[int, str]:
    body = _body(text)
    m = re.search(r"(\d+)\s*\(", body)
    return int(m.group(1)), body[m.end():body.rindex(")")]


def read_points(mesh: Path) -> np.ndarray:
    n, body = _list(_read(mesh / "points"))
    pts = np.array(re.findall(r"\(([^()]*)\)", body), dtype=object)
    arr = np.array([list(map(float, p.split())) for p in pts])
    assert arr.shape == (n, 3)
    return arr


def read_faces(mesh: Path) -> list[list[int]]:
    n, body = _list(_read(mesh / "faces"))
    faces = [list(map(int, f.split())) for f in re.findall(r"\d+\s*\(([^()]*)\)", body)]
    assert len(faces) == n
    return faces


def read_labels(mesh: Path, name: str) -> np.ndarray:
    n, body = _list(_read(mesh / name))
    arr = np.array(body.split(), dtype=int)
    assert arr.size == n
    return arr


def read_boundary(mesh: Path) -> list[dict]:
    body = _body(_read(mesh / "boundary"))
    out = []
    for name, block in re.findall(r"(\w+)\s*\{([^}]*)\}", body):
        get = lambda k: re.search(rf"\b{k}\s+([^;]+);", block)  # noqa: E731
        out.append({"name": name, "type": get("type").group(1).strip(),
                    "inGroups": (get("inGroups").group(1).strip() if get("inGroups") else None),
                    "nFaces": int(get("nFaces").group(1)), "startFace": int(get("startFace").group(1))})
    return out


def hexes(points, faces, owner, neighbour) -> np.ndarray:
    ncell = int(max(owner.max(), neighbour.max() if neighbour.size else -1)) + 1
    cell_faces: list[list[int]] = [[] for _ in range(ncell)]
    for f, c in enumerate(owner):
        cell_faces[c].append(f)
    for f, c in enumerate(neighbour):
        cell_faces[c].append(f)
    out = np.empty((ncell, 8), dtype=int)
    for c, fl in enumerate(cell_faces):
        if len(fl) != 6 or any(len(faces[f]) != 4 for f in fl):
            raise ValueError(f"cell {c} is not a hexahedron")
        quads = [faces[f] for f in fl]
        bottom = quads[0]
        edges = set()
        for q in quads:
            for i in range(4):
                a, b = q[i], q[(i + 1) % 4]
                edges.add((a, b)); edges.add((b, a))
        verts = {v for q in quads for v in q}
        top = []
        for v in bottom:
            nb = [w for w in verts - set(bottom) if (v, w) in edges]
            assert len(nb) == 1, f"cell {c}: cannot pair vertex {v}"
            top.append(nb[0])
        h = bottom + top
        p = points[h]
        vol = np.dot(np.cross(p[1] - p[0], p[3] - p[0]), p[4] - p[0])
        if vol < 0:
            h = [bottom[0], bottom[3], bottom[2], bottom[1], top[0], top[3], top[2], top[1]]
        out[c] = h
    return out


def write_msh22(path: Path, points, cells, patches, faces) -> None:
    lines = ["$MeshFormat", "2.2 0 8", "$EndMeshFormat", "$PhysicalNames", str(len(patches) + 1)]
    for i, p in enumerate(patches, start=1):
        lines.append(f'2 {i} "{p["name"]}"')
    vol_tag = len(patches) + 1
    lines.append(f'3 {vol_tag} "fluid"')
    lines += ["$EndPhysicalNames", "$Nodes", str(len(points))]
    lines += [f"{i + 1} {x:.17g} {y:.17g} {z:.17g}" for i, (x, y, z) in enumerate(points)]
    lines += ["$EndNodes", "$Elements"]
    elems = []
    for i, p in enumerate(patches, start=1):
        for f in range(p["startFace"], p["startFace"] + p["nFaces"]):
            elems.append(f"3 2 {i} {i} " + " ".join(str(v + 1) for v in faces[f]))
    for h in cells:
        elems.append(f"5 2 {vol_tag} {vol_tag} " + " ".join(str(v + 1) for v in h))
    lines.append(str(len(elems)))
    lines += [f"{k + 1} {e}" for k, e in enumerate(elems)]
    lines.append("$EndElements")
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    case, out = Path(sys.argv[1]), Path(sys.argv[2])
    mesh = case / "constant" / "polyMesh"
    pts = read_points(mesh)
    faces = read_faces(mesh)
    owner, neighbour = read_labels(mesh, "owner"), read_labels(mesh, "neighbour")
    patches = read_boundary(mesh)
    cells = hexes(pts, faces, owner, neighbour)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_msh22(out, pts, cells, patches, faces)
    meta = {"source": "OpenFOAM polyMesh", "format": "Gmsh MSH 2.2 ASCII",
            "n_points": len(pts), "n_hex": len(cells),
            "patches": [{k: p[k] for k in ("name", "type", "inGroups", "nFaces")} for p in patches],
            "volume_group": "fluid"}
    out.with_suffix(".patches.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps({k: meta[k] for k in ("n_points", "n_hex")}), [p["name"] for p in patches])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
