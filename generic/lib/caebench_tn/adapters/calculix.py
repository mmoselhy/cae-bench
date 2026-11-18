"""CalculiX adapter: wraps the upstream packaging-track checks by import."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from sim_benchmark_verifier.calculix_interface import strip_generated
from sim_benchmark_verifier.csv_interface import run_entry_point
from sim_benchmark_verifier.detectors import TrialContext
from sim_benchmark_verifier.detectors.calculix import has_result_database, has_solver_evidence

from . import Evidence, register


class CalculiXAdapter:
    name = "calculix"
    tested = True
    tracks = ("csv_interface",)

    def validate_inputs(self, submission: Path) -> None:
        # Upstream checks only that the entry point exists; the core does that.
        return None

    def strip(self, work: Path, interface_files: tuple[str, ...],
              preserve: tuple[str, ...] = ()) -> list[str]:
        if preserve:
            raise ValueError("the CalculiX track never preserved generated paths upstream")
        return strip_generated(work, interface_files)

    def run(self, work: Path, command: str, *, timeout_s: int,
            log_path: Path) -> dict[str, Any]:
        return run_entry_point(work, command, timeout_s=timeout_s, log_path=log_path)

    def solver_evidence(self, work: Path) -> Evidence:
        ctx = TrialContext(case_dir=work, solver_label="calculix")
        detail = {
            "result_database": has_result_database(ctx),
            "any_solver_artifact": has_solver_evidence(ctx),
        }
        if detail["result_database"]:
            return Evidence("pass", "", detail)
        return Evidence(
            "fail",
            "the rerun left no CalculiX result database -- no .frd holding the model "
            "ccx assembled together with solved values"
            + (" (a CalculiX banner is present, so something wrote text and no results)"
               if detail["any_solver_artifact"] else ""),
            detail)


register(CalculiXAdapter())
