from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from pathology_cases.loader import CaseCardError, parse_case
from pathology_cases.smuggling import ParameterSmugglingError, scan_for_smuggling
from tests.conftest import minimal_payload


def test_parameters_key_is_refused(disclaimer: str) -> None:
    payload = deepcopy(minimal_payload(disclaimer))
    payload["parameters"] = {"k": 0.2}
    with pytest.raises(CaseCardError, match="refused non-parameter"):
        parse_case(payload)


def test_ode_params_key_is_refused(disclaimer: str) -> None:
    payload = deepcopy(minimal_payload(disclaimer))
    payload["candidate_mechanisms"][0]["ode_params"] = {"r": 1.1}
    with pytest.raises(CaseCardError, match="ode_params"):
        parse_case(payload)


def test_nstg_numeric_scale_is_refused(disclaimer: str) -> None:
    payload = deepcopy(minimal_payload(disclaimer))
    payload["nstg_touchpoints"][0]["constraint_hints"] = {
        "x_cap_scale": 0.8,
        "infection_risk_weight": 0.4,
    }
    with pytest.raises(CaseCardError, match="constraint_hints"):
        parse_case(payload)


def test_dose_string_is_refused(disclaimer: str) -> None:
    payload = deepcopy(minimal_payload(disclaimer))
    payload["candidate_mechanisms"][0]["statement"] = (
        "Give 10 mg/kg of a checkpoint-class agent every q3w."
    )
    with pytest.raises(CaseCardError, match="dose-like|schedule|refused"):
        parse_case(payload)


def test_numeric_leaf_is_refused(disclaimer: str) -> None:
    payload = deepcopy(minimal_payload(disclaimer))
    payload["disease"]["notes"] = 0.42  # type: ignore[assignment]
    with pytest.raises(CaseCardError, match="numeric leaf"):
        parse_case(payload)


def test_ec50_token_is_refused() -> None:
    with pytest.raises(ParameterSmugglingError, match="PK/PD"):
        scan_for_smuggling({"statement": "Fit an EC50 next."})


def test_yaml_fixture_smuggling(tmp_path: Path, disclaimer: str) -> None:
    payload = deepcopy(minimal_payload(disclaimer))
    payload["x_cap"] = 1.15
    path = tmp_path / "smuggled.yaml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    from pathology_cases.loader import load_case

    with pytest.raises(CaseCardError, match="x_cap"):
        load_case(path)


def test_extra_unknown_key_is_refused_by_schema(disclaimer: str) -> None:
    payload = deepcopy(minimal_payload(disclaimer))
    payload["secret_score"] = "still extra"
    with pytest.raises(CaseCardError):
        parse_case(payload)
