import json
from pathlib import Path

from complexity_science.cli import main
from complexity_science.honesty import banned_hits
from complexity_science.pipeline import run_pipeline
from complexity_science.reporting.report import write_report


def test_run_pipeline_end_to_end(tmp_path: Path):
    result = run_pipeline(
        archetype_id="exhausted_high_burden",
        conditions=["oncology_supportive", "anaemia"],
        horizon_days=14.0,
        allow_combinations=False,
        max_candidates=10,
    )
    assert result.hypotheses
    assert result.retrieval.hits
    assert result.falsification
    written = write_report(result, tmp_path / "report.json")
    payload = json.loads(written["json"].read_text(encoding="utf-8"))
    assert payload["schema"] == "complexity_science.report.v1"
    md = written["markdown"].read_text(encoding="utf-8")
    assert "Falsification checklist" in md
    assert "in-silico" in md.lower()
    assert not banned_hits(md)
    assert not banned_hits(json.dumps(payload))


def test_cli_run_smoke(tmp_path: Path):
    out = tmp_path / "cli.json"
    code = main(
        [
            "run",
            "--archetype",
            "inflammatory_fragile",
            "--conditions",
            "malaria,sickle_cell",
            "--horizon",
            "10",
            "--max-candidates",
            "8",
            "--no-combinations",
            "--out",
            str(out),
        ]
    )
    assert code == 0
    assert out.is_file()
    assert out.with_suffix(".md").is_file()
