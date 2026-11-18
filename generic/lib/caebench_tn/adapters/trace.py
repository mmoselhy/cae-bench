"""Cantera and PyBaMM adapters.

Upstream has no solver-file gate on these two tracks: "a real solve happened"
is established by the evaluator's clean-copy reproduction (inputs only, every
numeric artifact stripped) plus the physics gates it computes itself from the
mechanism / parameter set -- `initial_state_valid` for both, `ocv_consistent`
for PyBaMM. Those live in the track evaluators (`native_cantera`,
`native_pybamm`), which the core runs unchanged; these adapters read their
verdict back out of the evaluator's own detail, and add nothing and drop nothing.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import Evidence, register

# The upstream gate dimensions that together mean "this trace came out of a
# replayed solve of this system". Read, not re-decided.
_EVIDENCE_DIMS = {
    "cantera": ("clean_reproduction", "artifact_produced", "initial_state_valid"),
    "pybamm": ("clean_reproduction", "artifact_produced", "initial_state_valid",
               "ocv_consistent"),
}


class _TraceAdapter:
    tested = True

    def __init__(self, name: str, track: str):
        self.name = name
        self.tracks = (track,)

    # The track evaluator owns validation, stripping and the replay.
    def validate_inputs(self, submission: Path) -> None:
        return None

    def strip(self, work: Path, interface_files: tuple[str, ...],
              preserve: tuple[str, ...] = ()) -> list[str]:
        raise NotImplementedError("the trace track evaluator strips its own copy")

    def run(self, work: Path, command: str, *, timeout_s: int,
            log_path: Path) -> dict[str, Any]:
        raise NotImplementedError("the trace track evaluator runs its own replay")

    def solver_evidence(self, work: Path) -> Evidence:
        raise NotImplementedError("use evidence_from_detail")

    def evidence_from_detail(self, detail: dict[str, Any]) -> Evidence:
        dims = detail.get("dimensions", {})
        seen = {d: dims.get(d, {}).get("status", "not_attempted") for d in _EVIDENCE_DIMS[self.name]}
        failed = [d for d, s in seen.items() if s != "pass"]
        if not failed:
            return Evidence("pass", "", seen)
        return Evidence("fail", "upstream gate(s) not passed: " + ", ".join(failed), seen)


register(_TraceAdapter("cantera", "cantera_trace"))
register(_TraceAdapter("pybamm", "pybamm_trace"))
