"""Write neutral sources for the template-generated combustion and battery cases.

    python3 generic/tools/neutralize_trace.py combustion|battery [--param-sentence TEXT]

Only cases whose instruction.md has the standard section layout are handled;
the hand-written special cases are skipped and listed.
"""
import json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GEN = REPO / "generic" / "cases"

MECH = {  # native name -> (shared input id, neutral description)
    "gri30.yaml": ("gri30", "GRI-Mech 3.0 (53 species, 325 reactions)"),
    "h2o2.yaml": ("h2o2", "the 10-species hydrogen/oxygen mechanism derived from GRI-Mech 3.0 (H2/O2 subset with Ar)"),
    "nDodecane_Reitz.yaml": ("ndodecane_reitz", "the reduced 100-species n-dodecane mechanism of Reitz and co-workers"),
    "example_data/ammonia-CO-H2-Alzueta-2023.yaml": ("nh3_co_h2_alzueta2023", "the 42-species ammonia/CO/H2 mechanism of Alzueta et al. (2023)"),
    "example_data/n-hexane-NUIG-2015.yaml": ("nhexane_nuig2015", "the NUIG n-hexane mechanism (Zhang et al., 2015; 1268 species)"),
}
PARAMS = {  # native name -> neutral description
    "Ai2020": "Ai et al. (2020): LCO / graphite pouch cell (Enertech)",
    "Chen2020": "Chen et al. (2020): LG M50 NMC811 / graphite-SiOx cylindrical cell",
    "Ecker2015": "Ecker et al. (2015): Kokam NMC / graphite pouch cell",
    "Marquis2019": "Marquis et al. (2019): Kokam LCO / graphite pouch cell",
    "Mohtat2020": "Mohtat et al. (2020): NMC532 / graphite pouch cell",
    "NCA_Kim2011": "Kim et al. (2011): NCA / graphite cell",
    "OKane2022": "O'Kane et al. (2022): LG M50 NMC811 / graphite-SiOx cell, with degradation parameters",
    "ORegan2022": "O'Regan et al. (2022): LG M50 NMC811 / graphite-SiOx cell, thermally characterised",
    "Prada2013": "Prada et al. (2013): A123 LFP / graphite cylindrical cell",
}
STANDARD = {
    "combustion": "## Conditions|## What to produce|## Environment|",
    "battery": "## Cell and operating point|## Protocol|## What to produce|## Environment|",
}


def sections(text):
    return "".join(l + "|" for l in re.findall(r"(?m)^## .*$", text))


def split_produce(text):
    head, rest = text.split("## What to produce", 1)
    produce, env = rest.split("## Environment", 1)
    return head.rstrip() + "\n", produce, env.strip()


def outputs_from(produce, driver="run_case.py"):
    budget = int(re.search(r"finish within (\d+) seconds", produce).group(1))
    items = re.split(r"(?m)^(?=\d+\. \*\*)", produce)
    kept, figure = [], False
    for it in items:
        if it.startswith("1. **`run_case.py`**") or not re.match(r"\d+\. ", it):
            continue
        if "**a figure**" in it:
            figure = True
            continue
        it = re.sub(r"^\d+\. ", "- ", it)
        it = re.sub(r"written by\s+`run_case\.py`", "written by `replay.sh`", it)
        kept.append(it.rstrip())
    return "\n\n".join(kept) + "\n", budget, figure


def toml_str(s):
    return json.dumps(s)


def write(rel, prompt, env_md, case):
    d = GEN / rel
    (d / "env").mkdir(parents=True, exist_ok=True)
    (d / "prompt.md").write_text(prompt)
    (d / "env" / "opensource.md").write_text(env_md)
    lines = [f"original = {toml_str('cases/' + rel)}", f"track = {toml_str(case['track'])}",
             f"domain = {toml_str(case['domain'])}", f"requires = {json.dumps(case['requires'])}",
             f"portability = {toml_str(case['portability'])}",
             f"portability_reason = {toml_str(case['reason'])}",
             f"figure = {'true' if case['figure'] else 'false'}"]
    if case.get("shared_inputs"):
        lines.append("[shared_inputs]")
        for k, v in case["shared_inputs"].items():
            lines.append(f"{json.dumps(k)} = {json.dumps(v)}")
    (d / "case.toml").write_text("\n".join(lines) + "\n")


def combustion(case_dir):
    rel = str(case_dir.relative_to(REPO / "cases"))
    text = (case_dir / "instruction.md").read_text()
    spec = json.loads((case_dir / "tests" / "spec.json").read_text())
    head, produce, env = split_produce(text)
    mech = spec["mechanism"]
    mid, desc = MECH[mech]
    row = re.search(r"(?m)^\| reaction mechanism \| `[^`]+` \|$", head)
    head = head[:row.start()] + (f"| reaction mechanism | {desc}; supplied in Chemkin format under "
                                 f"`/tmp/agent/inputs/mechanism/` (`chem.inp`, `therm.dat`"
                                 + (", `tran.dat`" if spec["kind"] != "idt" else "") + ") |") + head[row.end():]
    outs, budget, figure = outputs_from(produce)
    prompt = (head + "\n## Output files\n\nWrite these into the submission root:\n\n" + outs +
              "\n## Time budget\n\nThe evaluator re-runs your `replay.sh` from a clean copy of the "
              f"submission under a hard limit of **{budget} seconds**; a run that overruns is scored "
              "zero however good the physics. How much refinement you can afford is therefore part "
              "of the problem.\n")
    phase = f" (gas phase `{spec['phase']}`)" if spec.get("phase") else ""
    env_md = (f"- The reaction mechanism is Cantera's `{mech}`{phase}. " + env.replace("\n", " ").replace("The mechanism named above", "It")
              + " The Chemkin files under `/tmp/agent/inputs/mechanism/` were exported from it with "
              "Cantera's `write_chemkin`.\n")
    kind = spec["kind"]
    if kind == "idt":
        cv = "constant-volume" in text
        req = ["kinetics.0d.const_volume" if cv else "kinetics.0d.const_pressure", "kinetics.mechanism.chemkin"]
        port, reason = "portable", ("Homogeneous 0-D ignition with the mechanism supplied and the delay "
                                    "definition fixed (max dT/dt); the reference is the Cantera oracle's "
                                    "value, but any stiff kinetics integrator with the same mechanism "
                                    "reproduces it far inside a 5% band.")
    else:
        req = ["flame.1d.freely_propagating", "flame.transport.mixture_averaged", "kinetics.mechanism.chemkin"]
        if "unity" in text.lower() and "lewis" in text.lower():
            req.append("flame.transport.unity_lewis")
        port, reason = "portable-after-calibration", (
            "Freely propagating 1-D flame with mixture-averaged transport and the mechanism supplied; the "
            "reference is Cantera's grid-converged value. Codes differ in mixture-averaged details "
            "(correction velocity, thermal diffusion) by around 1-3%, inside the 5% band but close "
            "enough that another code should be calibrated before its scores are trusted.")
    write(rel, prompt, env_md, {"track": "cantera_trace", "domain": "combustion", "requires": req,
                                "portability": port, "reason": reason, "figure": figure,
                                "shared_inputs": {"mechanism": f"mechanisms/{mid}"}})


def battery(case_dir, param_sentence):
    rel = str(case_dir.relative_to(REPO / "cases"))
    text = (case_dir / "instruction.md").read_text()
    spec = json.loads((case_dir / "tests" / "spec.json").read_text())
    head, produce, env = split_produce(text)
    ps = spec["parameter_set"]
    row = re.search(r"(?m)^\| parameter set \| `[^`]+` \|$", head)
    head = head[:row.start()] + f"| parameter set | {PARAMS[ps]}; {param_sentence} |" + head[row.end():]
    outs, budget, figure = outputs_from(produce)
    prompt = (head + "\n## Output files\n\nWrite these into the submission root:\n\n" + outs +
              "\n## Time budget\n\nThe evaluator re-runs your `replay.sh` from a clean copy of the "
              f"submission under a hard limit of **{budget} seconds**; a run that overruns is scored "
              "zero however good the physics. How much refinement you can afford is therefore part "
              "of the problem.\n")
    env_md = f"- The parameter set is PyBaMM's `{ps}`. " + env.replace("\n", " ").replace("The parameter set named above", "It") + "\n"
    low = text.lower()
    req = []
    if "single representative particle" in low or "single particle" in low:
        req.append("echem.spme" if "electrolyte" in low else "echem.spm")
    else:
        req.append("echem.dfn")
    if spec["kind"] == "thermal" or "lumped" in low or "thermal model" in low:
        req.append("echem.thermal.lumped")
    if "sei" in low or "solid-electrolyte interphase" in low:
        req.append("echem.aging.sei")
    if "plating" in low:
        req.append("echem.aging.plating")
    req.append("echem.params.bpx")
    reason = ("The reference is PyBaMM's own output for this named model and parameter set (gt_type "
              "high-fidelity-solver). Another electrochemical code solves the same model class but with "
              "its own discretisation and model variants, and must be calibrated before its scores are "
              "trusted.")
    if spec["kind"] in ("cycling",):
        reason = ("The reference is PyBaMM's output with its specific SEI / lithium-plating submodels; other "
                  "codes implement different degradation laws, so equivalence must be calibrated per tool "
                  "and may not exist at all.")
    write(rel, prompt, env_md, {"track": "pybamm_trace", "domain": "battery", "requires": req,
                                "portability": "portable-after-calibration", "reason": reason,
                                "figure": figure})


if __name__ == "__main__":
    domain = sys.argv[1]
    sentence = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--param-sentence" else None
    skipped = []
    for inst in sorted((REPO / "cases" / domain).rglob("instruction.md")):
        if sections(inst.read_text()) != STANDARD[domain]:
            skipped.append(str(inst.parent.relative_to(REPO)))
            continue
        combustion(inst.parent) if domain == "combustion" else battery(inst.parent, sentence)
    print("skipped (hand-written):", *skipped, sep="\n  ")
