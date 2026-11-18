"""OpenFOAM adapter: wraps the upstream cfd-track checks, imported, not copied.

Every predicate below is the one `sim_benchmark_verifier.openfoam_interface`
gates on upstream; only the entry-point name differs (`replay.sh` instead of
`Allrun`), and that is the core's business, not this adapter's.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from sim_benchmark_verifier.detectors import TrialContext
from sim_benchmark_verifier.detectors.openfoam import (
    has_mesh_and_solution,
    has_solver_evidence,
    mesh_and_solution_files_present,
)
from sim_benchmark_verifier.native_openfoam import (
    CASE_INPUT_DIRECTORIES,
    case_input_roots,
    openfoam_command,
)
from sim_benchmark_verifier.openfoam_interface import strip_generated

from . import Evidence, InvalidSubmission, register


class OpenFOAMAdapter:
    name = "openfoam"
    tested = True
    tracks = ("csv_interface",)

    def validate_inputs(self, submission: Path) -> None:
        # Upstream `native_openfoam.validate_submission` minus the `Allrun`
        # half, which the core checks as `replay.sh`.
        if not case_input_roots(submission):
            raise InvalidSubmission(
                "missing reproducible case inputs: a case directory holding "
                + ", ".join(f"{n}/" for n in CASE_INPUT_DIRECTORIES))

    def strip(self, work: Path, interface_files: tuple[str, ...],
              preserve: tuple[str, ...] = ()) -> list[str]:
        return strip_generated(work, interface_files, preserve)

    def run(self, work: Path, command: str, *, timeout_s: int,
            log_path: Path) -> dict[str, Any]:
        return openfoam_command(work, command, timeout_s=timeout_s, log_path=log_path)

    def solver_evidence(self, work: Path) -> Evidence:
        ctx = TrialContext(case_dir=work, solver_label="openfoam")
        detail = {
            "mesh_and_solution": has_mesh_and_solution(ctx),
            "mesh_and_solution_files_present": mesh_and_solution_files_present(ctx),
            "any_solver_artifact": has_solver_evidence(ctx),
        }
        if detail["mesh_and_solution"]:
            return Evidence("pass", "", detail)
        if detail["mesh_and_solution_files_present"]:
            why = ("files named points/faces/<field> are there and do not read as "
                   "OpenFOAM output -- a wrong class, or a list shorter than its "
                   "own declared count")
        elif detail["any_solver_artifact"]:
            why = "a solver log is present, so something ran and wrote no field"
        else:
            why = "nothing the solver writes is there at all"
        return Evidence("fail", "the rerun left no OpenFOAM solution -- no serialised "
                        "polyMesh/ with a non-zero time directory holding a field "
                        f"({why})", detail)


register(OpenFOAMAdapter())
