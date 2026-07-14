import pytest

from waterfall_engine.engine.allocation import (
    allocate_lp_distributions,
    allocate_pro_rata,
)
from waterfall_engine.models.lp import LPCommitment
from waterfall_engine.validators.validator import WaterfallValidationError

# Mock dataset §2.7 — Meridian's 10-LP roster, pro-rata by fund commitment %.
MERIDIAN_LP_ROSTER = [
    LPCommitment(lp_id="LP-001", lp_name="LP-001", commitment_amount=75_000_000),
    LPCommitment(lp_id="LP-002", lp_name="LP-002", commitment_amount=50_000_000),
    LPCommitment(lp_id="LP-003", lp_name="LP-003", commitment_amount=100_000_000),
    LPCommitment(lp_id="LP-004", lp_name="LP-004", commitment_amount=25_000_000),
    LPCommitment(lp_id="LP-005", lp_name="LP-005", commitment_amount=50_000_000),
    LPCommitment(lp_id="LP-006", lp_name="LP-006", commitment_amount=30_000_000),
    LPCommitment(lp_id="LP-007", lp_name="LP-007", commitment_amount=25_000_000),
    LPCommitment(lp_id="LP-008", lp_name="LP-008", commitment_amount=40_000_000),
    LPCommitment(lp_id="LP-009", lp_name="LP-009", commitment_amount=30_000_000),
    LPCommitment(lp_id="LP-010", lp_name="LP-010", commitment_amount=25_000_000),
]
MERIDIAN_LP_TOTAL = 313_600_000
MERIDIAN_EXPECTED = {
    "LP-001": 52_266_667,
    "LP-002": 34_844_444,
    "LP-003": 69_688_889,
    "LP-004": 17_422_222,
    "LP-005": 34_844_444,
    "LP-006": 20_906_667,
    "LP-007": 17_422_222,
    "LP-008": 27_875_556,
    "LP-009": 20_906_667,
    "LP-010": 17_422_222,
}


def test_synthetic_roster_sums_exactly_and_matches_weights():
    weights = {"LP-A": 1, "LP-B": 1, "LP-C": 1}

    result = allocate_pro_rata(100, weights)

    assert sum(result.values()) == 100
    for amount in result.values():
        assert amount == pytest.approx(33.33, abs=0.02)  # one recipient absorbs the leftover cent


def test_synthetic_roster_uneven_weights_sums_exactly():
    weights = {"LP-A": 75_000_000, "LP-B": 50_000_000, "LP-C": 100_000_000, "LP-D": 25_000_000}
    total = 313_600_000

    result = allocate_pro_rata(total, weights)

    assert sum(result.values()) == total
    total_weight = sum(weights.values())
    for lp_id, weight in weights.items():
        assert result[lp_id] == pytest.approx(total * weight / total_weight, abs=0.01)


def test_allocate_lp_distributions_matches_meridian_roster():
    allocations = allocate_lp_distributions(MERIDIAN_LP_TOTAL, MERIDIAN_LP_ROSTER)

    assert sum(a.amount for a in allocations) == MERIDIAN_LP_TOTAL
    for allocation in allocations:
        expected = MERIDIAN_EXPECTED[allocation.lp_id]
        assert allocation.amount == pytest.approx(expected, abs=1)


def test_empty_commitments_raises():
    with pytest.raises(WaterfallValidationError):
        allocate_lp_distributions(100, [])


def test_zero_commitment_amount_raises():
    commitments = [
        LPCommitment(lp_id="LP-001", lp_name="LP-001", commitment_amount=0),
        LPCommitment(lp_id="LP-002", lp_name="LP-002", commitment_amount=50),
    ]
    with pytest.raises(WaterfallValidationError):
        allocate_lp_distributions(100, commitments)
