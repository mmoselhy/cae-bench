"""Solver adapters: the only solver-specific code in the verifier.

An adapter answers three questions about an evaluator-owned clean copy of a
submission, and nothing else:

* `validate_inputs(submission)` -- is there something runnable for this solver?
  (raise `InvalidSubmission`).
* `strip(work, interface_files, preserve)` -- delete everything this solver
  writes, so the replay has to write it again.
* `solver_evidence(work)` -- after the replay, did a real solve happen?
  Returns an `Evidence` whose verdict is "pass", "fail" or "unverified".

Plus `run(work, command, timeout_s, log_path)` for any environment set-up the
solver needs around the replay command.

Every value of `tested` other than True is reported as "unverified" by the
core and scores zero: an adapter nobody could run against a real solver output
must never be able to pass a submission.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


class InvalidSubmission(RuntimeError):
    pass


@dataclass
class Evidence:
    verdict: str  # pass | fail | unverified
    why: str = ""
    detail: dict[str, Any] = field(default_factory=dict)


class SolverAdapter(Protocol):
    name: str
    tested: bool
    #: tracks this adapter can serve: "csv_interface", "cantera_trace", "pybamm_trace"
    tracks: tuple[str, ...]

    def validate_inputs(self, submission: Path) -> None: ...

    def strip(self, work: Path, interface_files: tuple[str, ...],
              preserve: tuple[str, ...] = ()) -> list[str]: ...

    def run(self, work: Path, command: str, *, timeout_s: int,
            log_path: Path) -> dict[str, Any]: ...

    def solver_evidence(self, work: Path) -> Evidence: ...


_REGISTRY: dict[str, SolverAdapter] = {}


def register(adapter: SolverAdapter) -> SolverAdapter:
    _REGISTRY[adapter.name] = adapter
    return adapter


def get(name: str | None) -> SolverAdapter | None:
    _load()
    return _REGISTRY.get((name or "").strip().lower())


def registered() -> dict[str, SolverAdapter]:
    _load()
    return dict(_REGISTRY)


_LOADED = False


def _load() -> None:
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    from . import calculix, openfoam, stubs, trace  # noqa: F401  (registration side effects)
