from complexity_science.nstg import NstgRetriever


def test_retriever_malaria_themes_and_cautions():
    result = NstgRetriever().retrieve("malaria")
    assert result.hits
    entry = result.hits[0].entry
    assert entry.id == "malaria"
    assert entry.themes
    assert entry.cautions
    assert "anaemia" in entry.comorbidities
    assert entry.status == "PLACEHOLDER_RESEARCH_INDEX"


def test_alias_and_merge_is_conservative():
    result = NstgRetriever().retrieve(["sickle cell", "HIV", "anaemia"])
    ids = {hit.entry.id for hit in result.hits}
    assert {"sickle_cell", "hiv", "anaemia"} <= ids
    hints = result.merged_hints()
    # min scale, max infection weight
    assert hints.x_cap_scale <= 0.85
    assert hints.infection_risk_weight >= 0.3
    assert "haemolytic_host" in hints.flags


def test_unmatched_recorded():
    result = NstgRetriever().retrieve("not-a-real-condition-xyz")
    assert result.unmatched
    assert result.provenance.get("cite")
