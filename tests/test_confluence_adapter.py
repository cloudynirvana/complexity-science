from complexity_science.integration.confluence_adapter import (
    SCHEMA_ID,
    EXAMPLE_REQUEST,
    execute_request,
    parse_request,
    to_confluence_payload,
)
from complexity_science.pipeline import run_pipeline


def test_parse_and_execute_contract():
    req = parse_request(EXAMPLE_REQUEST)
    assert req.archetype_id == "comorbidity_constrained"
    assert "malaria" in req.conditions
    payload = execute_request(
        {
            "schema": SCHEMA_ID,
            "request_id": "test-1",
            "query": {
                "archetype_id": "exhausted_high_burden",
                "conditions": ["hiv"],
                "horizon_days": 10,
                "search": {"max_candidates": 6, "allow_combinations": False},
            },
        }
    )
    assert payload["schema"] == SCHEMA_ID
    assert payload["status"] == "ok"
    assert payload["request_id"] == "test-1"
    assert "disclaimer" in payload
    assert payload["result"]["hypotheses"]


def test_local_wrap_has_no_confluence_import():
    result = run_pipeline(
        conditions=["anaemia"],
        horizon_days=8.0,
        allow_combinations=False,
        max_candidates=5,
    )
    wrapped = to_confluence_payload(result, request_id="local-test")
    assert wrapped["status"] == "ok"
    # seam stays contract-only
    import complexity_science.integration.confluence_adapter as adapter

    source = adapter.__file__
    text = open(source, encoding="utf-8").read()
    assert "import confluence" not in text.lower()
    assert "flybody" not in text.lower()
