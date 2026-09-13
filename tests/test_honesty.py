import pytest

from complexity_science.honesty import (
    DISCLAIMER_SHORT,
    NON_CLAIMS,
    assert_honest,
    banned_hits,
)


def test_disclaimer_and_non_claims_are_clean():
    assert "not a medical device" in DISCLAIMER_SHORT.lower()
    assert not banned_hits(DISCLAIMER_SHORT)
    assert not banned_hits("\n".join(NON_CLAIMS))


def test_banned_phrasing_rejected():
    assert banned_hits("this is clinically validated tomorrow")
    with pytest.raises(ValueError, match="banned"):
        assert_honest("FDA-ready package")
    assert not banned_hits("awaiting external validation; in-silico hypothesis")
    assert not banned_hits("Does not claim clinical validation, Phase II status.")
