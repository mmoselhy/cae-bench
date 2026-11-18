"""Unit tests for CAE-bench-TN that need no solver and no Docker.

The solver-backed checks (oracle parity, negative controls through Harbor)
are the gates in `caebench_tn.gates`; these cover the logic around them.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

LIB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LIB))

from caebench_tn import adapters, contract, core, generate  # noqa: E402

REPO = generate.REPO
PILOTS = ["cfd/fluids/lid_driven_cavity_ghia_re1000",
          "packaging/thermal/pkg25d_thermal_tim118um_k4p7_h22600"]

# Words that name a tool, a tool's file layout or a tool's data set. None may
# appear in a NEUTRAL prompt (prompt.md); a profile appendix may carry them.
TOOL_TOKENS = [
    "openfoam", "calculix", r"\bccx\b", r"gmsh(?! msh)", "cantera", "pybamm", "blockmesh",
    "simplefoam", "pimplefoam", "icofoam", "buoyant", "polymesh", "allrun", "run_case",
    r"gri30\.yaml", r"\.yaml\b", "chen2020", "ecker2015", "marquis2019", "okane2022",
    "prada2013", "ramadass2004", "mohtat2020", "ai2020", r"\bsystem/", r"\bconstant/",
    r"\.frd\b", r"(?<!chem)\.inp\b", "fvschemes", "fvsolution", "controldict", "sampledict",
]


# ── contract ────────────────────────────────────────────────────────────────

def _write_contract(sub: Path, **over) -> None:
    data = {"solver": {"name": "calculix", "version": "2.17"}, "replay": "replay.sh",
            "native_results": [], "kpis": {}}
    data.update(over)
    (sub / "result.json").write_text(json.dumps(data))
    (sub / "replay.sh").write_text("#!/bin/bash\ntrue\n")


def test_missing_result_json_is_invalid(tmp_path):
    c = contract.load(tmp_path)
    assert not c.ok and "missing" in c.problems[0]


def test_valid_contract(tmp_path):
    _write_contract(tmp_path)
    c = contract.load(tmp_path)
    assert c.ok, c.problems
    assert c.solver_name == "calculix"


def test_contract_requires_version_and_replay(tmp_path):
    (tmp_path / "result.json").write_text(json.dumps({"solver": {"name": "calculix"}}))
    c = contract.load(tmp_path)
    assert not c.ok
    assert any("version" in p for p in c.problems)
    assert any("replay.sh missing" in p for p in c.problems)


# ── adapter selection: unknown or stub => unverified, never pass ───────────

TN = {"case_id": "x", "profile": "p", "track": "csv_interface", "domain": "packaging",
      "solvers": ["calculix", "starccm", "optistruct", "simcenter-nastran", "mystery"]}


@pytest.mark.parametrize("name", ["starccm", "optistruct", "simcenter-nastran"])
def test_stub_adapters_are_unverified(tmp_path, name):
    _write_contract(tmp_path, solver={"name": name, "version": "1"})
    adapter, why = core.select_adapter(contract.load(tmp_path), TN)
    assert adapter is None and "untested stub" in why


def test_unknown_solver_is_unverified(tmp_path):
    _write_contract(tmp_path, solver={"name": "mystery", "version": "1"})
    adapter, why = core.select_adapter(contract.load(tmp_path), TN)
    assert adapter is None and "no adapter" in why


def test_solver_not_in_profile_is_unverified(tmp_path):
    _write_contract(tmp_path, solver={"name": "openfoam", "version": "v2412"})
    adapter, why = core.select_adapter(contract.load(tmp_path), TN)
    assert adapter is None and "not offered by profile" in why


def test_stub_evidence_never_passes(tmp_path):
    for name in ("starccm", "optistruct", "simcenter-nastran"):
        a = adapters.get(name)
        assert a is not None and a.tested is False
        assert a.solver_evidence(tmp_path).verdict == "unverified"


def test_every_tested_adapter_is_one_of_the_four():
    tested = {n for n, a in adapters.registered().items() if a.tested}
    assert tested == {"openfoam", "calculix", "cantera", "pybamm"}


# ── end-to-end verifier on fabricated submissions (no solver needed) ────────

def _tests_dir(tmp_path: Path, rel: str, solvers: list[str]) -> Path:
    src = REPO / "cases" / rel / "tests"
    dst = tmp_path / "tests"
    shutil.copytree(src, dst)
    (dst / "tn.json").write_text(json.dumps({
        "case_id": json.loads((src / "spec.json").read_text())["case_id"],
        "profile": "opensource", "track": "csv_interface",
        "domain": rel.split("/")[0], "solvers": solvers}))
    return dst


def _printf_submission(sub: Path, solver: str) -> None:
    sub.mkdir(parents=True)
    spec = json.loads((REPO / "cases" / PILOTS[1] / "tests" / "spec.json").read_text())
    kpis = json.loads((REPO / "cases" / PILOTS[1] / "tests" / "kpis.json").read_text())["kpis"]
    cols = spec["interface"]["columns"]
    vals = ",".join(str(kpis[c]["gt_value"]) for c in cols)
    (sub / "replay.sh").write_text(f"#!/bin/bash\nprintf '%s\\n' '{','.join(cols)}' '{vals}' > results.csv\n")
    (sub / "result.json").write_text(json.dumps({"solver": {"name": solver, "version": "x"},
                                                 "replay": "replay.sh", "native_results": [], "kpis": {}}))


def test_printf_replay_scores_zero_on_calculix_track(tmp_path):
    tests = _tests_dir(tmp_path, PILOTS[1], ["calculix"])
    sub = tmp_path / "sub"
    _printf_submission(sub, "calculix")
    d = core.verify(tests, sub, tmp_path / "out")
    assert d["final_score"] == 0.0
    assert d["failure_category"] == "invalid_physics_setup"
    assert json.loads((tmp_path / "out" / "reward.json").read_text()) == {"score": 0.0}


def test_stub_solver_scores_zero_and_reports_unverified(tmp_path):
    tests = _tests_dir(tmp_path, PILOTS[1], ["optistruct"])
    sub = tmp_path / "sub"
    _printf_submission(sub, "optistruct")
    d = core.verify(tests, sub, tmp_path / "out")
    assert d["final_score"] == 0.0
    assert d["verification"] == "unverified"
    assert d["failure_category"] == "unverified_solver"


def test_empty_submission_scores_zero(tmp_path):
    tests = _tests_dir(tmp_path, PILOTS[0], ["openfoam"])
    sub = tmp_path / "sub"
    sub.mkdir()
    d = core.verify(tests, sub, tmp_path / "out")
    assert d["final_score"] == 0.0 and d["failure_category"] == "contract_invalid"


def test_openfoam_inputs_required(tmp_path):
    tests = _tests_dir(tmp_path, PILOTS[0], ["openfoam"])
    sub = tmp_path / "sub"
    sub.mkdir()
    _write_contract(sub, solver={"name": "openfoam", "version": "v2412"})
    d = core.verify(tests, sub, tmp_path / "out")
    assert d["final_score"] == 0.0 and d["failure_category"] == "invalid_submission"


def test_claim_audit_is_diagnostic(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "k.csv").write_text("kpi,value\na,1.5\n")
    _write_contract(sub, kpis={"a": {"value": 1.5, "source": {
        "kind": "file_extract", "path": "/tmp/agent/submission/k.csv",
        "extract": "awk -F, '$1==\"a\" {print $2}'"}}})
    c = contract.load(sub)
    out = core.audit_claims(c, sub, ["a", "b"], {"a": 1.49}, {"a": 0.1})
    assert out["a"]["provenance_stage"] == "P4_pass"
    assert out["a"]["claim_within_pass_tol_of_evaluator"] is True
    assert out["b"]["provenance_stage"] == "P0_hallucination"


# ── generator ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def rendered(tmp_path_factory):
    out = tmp_path_factory.mktemp("dist")
    profile = generate.load_toml(generate.GENERIC / "profiles" / "opensource.toml")
    for src in generate.neutral_cases():
        generate.render_case(src, profile, out)
    return out


def test_every_neutral_prompt_is_tool_free():
    for src in generate.neutral_cases():
        text = (src / "prompt.md").read_text().lower()
        hits = [t for t in TOOL_TOKENS if re.search(t, text)]
        assert not hits, f"{src}: tool tokens in neutral prompt: {hits}"


def test_reference_files_are_byte_identical(rendered):
    for src in generate.neutral_cases():
        case = generate.load_toml(src / "case.toml")
        rel = Path(case["original"]).relative_to("cases")
        for name in ("kpis.json", "spec.json"):
            assert (rendered / rel / "tests" / name).read_bytes() == \
                   (REPO / case["original"] / "tests" / name).read_bytes()


def test_opensource_render_keeps_every_tool_fact_of_the_original(rendered):
    """Every tool token the original prompt uses also appears in the render."""
    for src in generate.neutral_cases():
        case = generate.load_toml(src / "case.toml")
        orig = (REPO / case["original"] / "instruction.md").read_text().lower()
        new = (rendered / Path(case["original"]).relative_to("cases") / "instruction.md").read_text().lower()
        lost = [t for t in TOOL_TOKENS
                if re.search(t, orig) and not re.search(t, new)
                and t not in ("allrun", "run_case")]  # the deliverable name is what changes
        assert not lost, f"{src}: opensource render lost tool facts {lost}"


def test_solution_and_tests_stay_out_of_the_agent_environment(rendered):
    for env in rendered.rglob("environment"):
        names = {p.name for p in env.rglob("*")}
        assert not names & {"solve.sh", "kpis.json", "spec.json", "tn.json", "test.sh"}, env


def test_rendered_task_names_use_variant_namespace(rendered):
    for t in rendered.rglob("task.toml"):
        assert re.search(r'(?m)^name\s*=\s*"caebench-tn/', t.read_text()), t


def test_inputs_are_planted_from_tests_not_submission(tmp_path, monkeypatch):
    tests = tmp_path / "tests"
    (tests / "inputs" / "mechanism").mkdir(parents=True)
    (tests / "inputs" / "mechanism" / "chem.inp").write_text("ELEMENTS\nEND\n")
    dst = tmp_path / "agent_inputs"
    monkeypatch.setenv("SIM_BENCH_INPUTS", str(dst))
    out = core.plant_inputs(tests)
    assert out["planted"] and (dst / "mechanism" / "chem.inp").read_text().startswith("ELEMENTS")
    assert core.plant_inputs(tmp_path / "nothing")["planted"] is False
