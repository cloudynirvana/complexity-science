from __future__ import annotations

import ast
from pathlib import Path

from pathology_cases.loader import iter_case_paths, load_case, parse_case
from pipeline.explorer import explore, explore_all
from pipeline.sketches import PathwaySketch
from tests.conftest import CASES, ROOT, minimal_payload


def test_explorer_emits_gated_sketches_for_all_seeds() -> None:
    sketches = explore_all(CASES)
    assert {item.case_id for item in sketches} == {
        path.stem for path in iter_case_paths(CASES)
    }
    for sketch in sketches:
        assert isinstance(sketch, PathwaySketch)
        assert sketch.ranked_hypotheses
        assert sketch.required_evidence
        assert sketch.refused_non_parameters
        assert sketch.nstg_constraints
        assert "Knowledge" in sketch.epistemic_boundary
        kinds = {item.attempted_kind for item in sketch.refused_non_parameters}
        assert "nstg_scale" in kinds
        assert "parameter" in kinds
        assert "prediction" in kinds
        for hypothesis in sketch.ranked_hypotheses:
            assert hypothesis.parameter_status == "refused"
            assert hypothesis.prediction_status == "not_emitted"
            assert hypothesis.required_evidence


def test_contributor_yaml_does_not_need_ode(tmp_path: Path, disclaimer: str) -> None:
    payload = parse_case(minimal_payload(disclaimer))
    path = tmp_path / "new_complex_case.yaml"
    path.write_text(
        # Round-trip through the object so the contributor file is data-only.
        __import__("yaml").safe_dump(payload.model_dump(), sort_keys=False),
        encoding="utf-8",
    )
    sketch = explore(load_case(path))
    assert sketch.case_id == "test_minimal_card"
    assert all(h.parameter_status == "refused" for h in sketch.ranked_hypotheses)


def test_research_score_is_not_a_parameter() -> None:
    card = load_case(CASES / "tnbc_metabolic_immune_exclusion.yaml")
    sketch = explore(card)
    assert "effect size" in " ".join(sketch.notes).lower()
    dumped = sketch.to_dict()
    assert "ode" not in str(dumped).lower() or "no ode" in str(dumped).lower()


def _python_files(package: str) -> list[Path]:
    return list((ROOT / package).rglob("*.py"))


def test_packages_do_not_import_ode_or_scipy() -> None:
    banned = {"numpy", "scipy", "ode", "dynamics"}
    for package in ("pathology_cases", "pipeline"):
        for path in _python_files(package):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = {alias.name.split(".")[0] for alias in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = {node.module.split(".")[0]}
                else:
                    continue
                overlap = names & banned
                assert not overlap, f"{path} imports {overlap}"
