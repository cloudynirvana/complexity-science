from complexity_science.biologics.catalog import load_catalog
from complexity_science.biologics.constraints import build_constraints
from complexity_science.biologics.search import search_pathways
from complexity_science.dynamics.archetypes import get_archetype
from complexity_science.nstg import NstgRetriever


def test_catalog_has_four_classes():
    ids = {item.id for item in load_catalog()}
    assert ids == {
        "checkpoint_pd1_like",
        "tgfb_trap_like",
        "cytokine_like",
        "fusion_mab_like",
    }
    for item in load_catalog():
        assert item.provenance.get("kind") == "class_literature"
        assert "not" in item.provenance


def test_search_returns_ranked_hypotheses_with_checklist_fields():
    arch = get_archetype("comorbidity_constrained")
    retrieval = NstgRetriever().retrieve(["malaria", "hiv"])
    constraints = build_constraints(retrieval)
    hyps = search_pathways(
        arch,
        constraints,
        horizon_days=14.0,
        allow_combinations=False,
        max_candidates=12,
    )
    assert hyps
    assert hyps[0].rank == 1
    assert "b_final" in hyps[0].metrics
    assert "burden" in hyps[0].objectives
    assert hyps[0].label
    # untreated baseline is present and not labelled as advice
    labels = [h.label for h in hyps]
    assert any("untreated" in label for label in labels)
