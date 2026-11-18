"""UNTESTED STUBS for commercial solvers. They never pass a submission.

No Siemens or Altair installation, licence or sample output was available when
these were written, so no file format is parsed here: inventing a parser that
cannot be run against real output would make "a real solve happened" an
untested claim. Every method that would need such parsing returns
`Evidence("unverified")`, which the core scores as 0 with
`failure_category = "unverified_solver"`.

To make one real: implement `strip` and `solver_evidence` against genuine
solver output, add calibration fixtures (one healthy run, one fabricated
`results.csv` with no solve) under `generic/lib/tests/fixtures/<solver>/`,
prove the healthy one passes and the fabricated one fails, and only then set
`tested = True`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from sim_benchmark_verifier.csv_interface import run_entry_point

from . import Evidence, register


class _UntestedStub:
    tested = False
    tracks = ("csv_interface",)

    def __init__(self, name: str, todo: str):
        self.name = name
        self.todo = todo

    def validate_inputs(self, submission: Path) -> None:
        return None

    def strip(self, work: Path, interface_files: tuple[str, ...],
              preserve: tuple[str, ...] = ()) -> list[str]:
        # TODO: delete every file the solver writes (see `todo`). Until then only
        # the interface file is removed, which is NOT enough to force a re-solve.
        removed = []
        for name in interface_files:
            for p in [work / name, *work.rglob(name)]:
                if p.is_file():
                    p.unlink()
                    removed.append(str(p.relative_to(work)))
        return removed

    def run(self, work: Path, command: str, *, timeout_s: int,
            log_path: Path) -> dict[str, Any]:
        return run_entry_point(work, command, timeout_s=timeout_s, log_path=log_path)

    def solver_evidence(self, work: Path) -> Evidence:
        return Evidence("unverified", f"{self.name} adapter is an untested stub. TODO: {self.todo}")


register(_UntestedStub(
    "starccm",
    "STAR-CCM+: strip *.sim results / *.csv reports written by the macro; require a "
    "saved .sim whose solution history shows iterations > 0 (or an exported report "
    "written by this replay). Needs real .sim fixtures to calibrate."))
register(_UntestedStub(
    "simcenter-nastran",
    "Simcenter 3D / Nastran: strip *.op2 *.f06 *.f04 *.log *.xdb; require an .f06 with "
    "a completed-run marker and solution tables for the requested SOL, or an .op2 with "
    "result blocks. Needs real .op2/.f06 fixtures to calibrate."))
register(_UntestedStub(
    "optistruct",
    "OptiStruct: strip *.h3d *.op2 *.out *.stat *.res; require an .out reporting "
    "successful completion and an .h3d/.op2 with result datasets. Needs real fixtures "
    "to calibrate."))
