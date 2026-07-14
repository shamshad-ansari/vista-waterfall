from datetime import date

import pytest
from mock_data.lookups import UnknownAssetError

from valuation_mcp.reasoning import ValuationReasoningError, value_asset
from valuation_mcp.schemas.valuation import ValuationInput

ASSET_ID = "MSC-2019-047"


def test_meridian_golden_path_demo_price_feed():
    """No closing_price_per_unit supplied -> falls back to mock_data.get_price_feed_response."""
    result = value_asset(ValuationInput(asset_id=ASSET_ID))

    assert result.confirmed_total_valuation == 340_000_000
    assert result.valuation_per_unit == 34.00
    assert result.tranche_values == {
        "MSC-T1": 153_000_000,
        "MSC-T2": 85_000_000,
        "MSC-T3": 102_000_000,
    }
    assert result.prior_total_carrying_value == 206_500_000
    assert result.valuation_uplift == 133_500_000
    assert result.validation_status == "PASSED — 5 of 5 checks"
    assert all(check.passed for check in result.validation_checks)
    assert len(result.validation_checks) == 5
    assert result.methodology == "negotiated_transaction_price"
    assert result.effective_date == date(2026, 6, 1)
    assert result.source_tool == "Acme Price Feed (customer-registered)"


def test_meridian_golden_path_explicit_price_feed_input():
    """Same scenario, but with the price-feed fields supplied directly on the input
    (mirroring what an externally-registered Tool B would hand the agent)."""
    result = value_asset(
        ValuationInput(
            asset_id=ASSET_ID,
            closing_price_per_unit=34.00,
            methodology="negotiated_transaction_price",
            ic_approved_by="Investment Committee — 2026-05-28",
            effective_date=date(2026, 6, 1),
            arm_length_confirmation=True,
        )
    )

    assert result.confirmed_total_valuation == 340_000_000
    assert result.tranche_values["MSC-T1"] == 153_000_000
    assert result.tranche_values["MSC-T2"] == 85_000_000
    assert result.tranche_values["MSC-T3"] == 102_000_000
    assert result.valuation_uplift == 133_500_000
    assert result.validation_status == "PASSED — 5 of 5 checks"
    assert result.source_tool == "Customer-registered price feed"


def test_uplift_percentage_matches_spec_display_figure():
    result = value_asset(ValuationInput(asset_id=ASSET_ID))

    uplift_check = next(c for c in result.validation_checks if c.name == "uplift_within_sane_range")
    assert uplift_check.passed
    assert "+15.3%" in uplift_check.detail or "+15.2%" in uplift_check.detail


def test_unknown_asset_raises():
    with pytest.raises(UnknownAssetError):
        value_asset(ValuationInput(asset_id="NOT-A-REAL-ASSET"))


def test_missing_arm_length_confirmation_fails_that_check():
    result = value_asset(
        ValuationInput(
            asset_id=ASSET_ID,
            closing_price_per_unit=34.00,
            methodology="negotiated_transaction_price",
            ic_approved_by="Investment Committee — 2026-05-28",
            effective_date=date(2026, 6, 1),
            arm_length_confirmation=False,
        )
    )

    assert result.validation_status.startswith("FAILED")
    arm_check = next(c for c in result.validation_checks if c.name == "arm_length_confirmed")
    assert not arm_check.passed


def test_missing_ic_approval_fails_that_check():
    result = value_asset(
        ValuationInput(
            asset_id=ASSET_ID,
            closing_price_per_unit=34.00,
            arm_length_confirmation=True,
            effective_date=date(2026, 6, 1),
        )
    )

    assert result.validation_status.startswith("FAILED")
    ic_check = next(c for c in result.validation_checks if c.name == "ic_approval_present")
    assert not ic_check.passed


def test_uplift_outside_sane_range_fails_that_check():
    """A wildly high price vs. the $29.50 prior mark should fail the uplift sanity check."""
    result = value_asset(
        ValuationInput(
            asset_id=ASSET_ID,
            closing_price_per_unit=200.00,
            methodology="negotiated_transaction_price",
            ic_approved_by="Investment Committee — 2026-05-28",
            effective_date=date(2026, 6, 1),
            arm_length_confirmation=True,
        )
    )

    uplift_check = next(c for c in result.validation_checks if c.name == "uplift_within_sane_range")
    assert not uplift_check.passed
    assert result.validation_status.startswith("FAILED")


def test_unpriced_tranche_missing_from_asset_raises():
    from mock_data.lookups import get_asset_record

    asset = get_asset_record(ASSET_ID)
    assert all(t.prior_mark_per_unit is None for t in asset.tranches) is False  # sanity: 2 of 3 are priced

    # Every tranche pre-priced would leave nothing to revalue.
    fully_priced = asset.model_copy(deep=True)
    for tranche in fully_priced.tranches:
        tranche.prior_mark_per_unit = 34.00

    import valuation_mcp.reasoning as reasoning_module

    with pytest.raises(ValuationReasoningError):
        reasoning_module._find_unpriced_tranche(fully_priced)
