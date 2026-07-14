"""Valuation Agent reasoning: implied enterprise value + tranche restatement.

Implements mock_datasets_Final_12pm.md SS1.4 — reasons across Tool A (Ledger
Data Tool, native — mock_data.get_asset_record) and Tool B (Price Feed Tool,
customer-registered — either supplied directly on the input, or resolved via
mock_data.get_price_feed_response as the demo stand-in).
"""

from mock_data.lookups import get_asset_record, get_price_feed_response
from mock_data.models import AssetRecord, TrancheRecord

from valuation_mcp.schemas.valuation import ValidationCheck, ValuationInput, ValuationOutput

UPLIFT_SANE_RANGE = 0.50  # +/-50% vs. weighted prior mark is plausible for a control-premium transaction


class ValuationReasoningError(ValueError):
    """Raised when the asset record doesn't have exactly one unpriced tranche to value."""


def _find_unpriced_tranche(asset: AssetRecord) -> TrancheRecord:
    unpriced = [t for t in asset.tranches if t.prior_mark_per_unit is None]
    if len(unpriced) != 1:
        raise ValuationReasoningError(
            f"Expected exactly one unpriced tranche on asset '{asset.asset_id}', found {len(unpriced)}"
        )
    return unpriced[0]


def _weighted_avg_prior_mark(priced_tranches: list[TrancheRecord]) -> float | None:
    priced_with_marks = [t for t in priced_tranches if t.prior_mark_per_unit is not None]
    if not priced_with_marks:
        return None
    total_units = sum(t.units_held for t in priced_with_marks)
    return sum(t.units_held * t.prior_mark_per_unit for t in priced_with_marks) / total_units


def _run_validation_checks(
    *,
    closing_price_per_unit: float | None,
    arm_length_confirmation: bool | None,
    ic_approved_by: str | None,
    units_transacted: float,
    unpriced_tranche: TrancheRecord,
    weighted_avg_prior_mark: float | None,
) -> list[ValidationCheck]:
    checks = []

    price_ok = closing_price_per_unit is not None and closing_price_per_unit > 0
    checks.append(
        ValidationCheck(
            name="price_present_positive",
            passed=price_ok,
            detail=f"closing_price_per_unit={closing_price_per_unit}",
        )
    )

    checks.append(
        ValidationCheck(
            name="arm_length_confirmed",
            passed=arm_length_confirmation is True,
            detail=f"arm_length_confirmation={arm_length_confirmation}",
        )
    )

    checks.append(
        ValidationCheck(
            name="ic_approval_present",
            passed=bool(ic_approved_by),
            detail=f"ic_approved_by={ic_approved_by!r}",
        )
    )

    if weighted_avg_prior_mark is None or closing_price_per_unit is None:
        uplift_pct = None
        uplift_ok = True
        uplift_detail = "no prior-marked tranches to compare against"
    else:
        uplift_pct = (closing_price_per_unit - weighted_avg_prior_mark) / weighted_avg_prior_mark
        uplift_ok = abs(uplift_pct) <= UPLIFT_SANE_RANGE
        uplift_detail = f"{uplift_pct:+.1%} vs. weighted prior mark ${weighted_avg_prior_mark:.2f}/unit"
    checks.append(
        ValidationCheck(name="uplift_within_sane_range", passed=uplift_ok, detail=uplift_detail)
    )

    units_ok = units_transacted == unpriced_tranche.units_held
    checks.append(
        ValidationCheck(
            name="units_reconcile_to_ledger",
            passed=units_ok,
            detail=f"{units_transacted} transacted vs. {unpriced_tranche.units_held} on ledger",
        )
    )

    return checks


def value_asset(payload: ValuationInput) -> ValuationOutput:
    """Run the Valuation Agent's end-to-end reasoning for a single asset."""

    asset = get_asset_record(payload.asset_id)
    unpriced_tranche = _find_unpriced_tranche(asset)
    priced_tranches = [t for t in asset.tranches if t.tranche_id != unpriced_tranche.tranche_id]

    if payload.closing_price_per_unit is not None:
        closing_price_per_unit = payload.closing_price_per_unit
        methodology = payload.methodology or "recent_transaction_price"
        ic_approved_by = payload.ic_approved_by
        effective_date = payload.effective_date
        arm_length_confirmation = payload.arm_length_confirmation
        effective_date = effective_date or unpriced_tranche.investment_date
        units_transacted = unpriced_tranche.units_held
        source_tool = "Customer-registered price feed"
    else:
        price_feed = get_price_feed_response(payload.asset_id, unpriced_tranche.tranche_id)
        closing_price_per_unit = price_feed.closing_price_per_unit
        methodology = price_feed.methodology
        ic_approved_by = price_feed.ic_approved_by
        effective_date = price_feed.transaction_date
        arm_length_confirmation = price_feed.arm_length_confirmation
        units_transacted = price_feed.units_transacted
        source_tool = "Acme Price Feed (customer-registered)"

    total_units = sum(t.units_held for t in asset.tranches)
    confirmed_total_valuation = closing_price_per_unit * total_units

    tranche_values = {t.tranche_id: t.units_held * closing_price_per_unit for t in asset.tranches}

    prior_total_carrying_value = sum(
        t.prior_carrying_value for t in priced_tranches if t.prior_carrying_value is not None
    )
    valuation_uplift = confirmed_total_valuation - prior_total_carrying_value

    weighted_avg_prior_mark = _weighted_avg_prior_mark(priced_tranches)
    checks = _run_validation_checks(
        closing_price_per_unit=closing_price_per_unit,
        arm_length_confirmation=arm_length_confirmation,
        ic_approved_by=ic_approved_by,
        units_transacted=units_transacted,
        unpriced_tranche=unpriced_tranche,
        weighted_avg_prior_mark=weighted_avg_prior_mark,
    )
    passed_count = sum(1 for c in checks if c.passed)
    if passed_count == len(checks):
        validation_status = f"PASSED — {passed_count} of {len(checks)} checks"
    else:
        failed_names = ", ".join(c.name for c in checks if not c.passed)
        validation_status = f"FAILED — {passed_count} of {len(checks)} checks passed (failed: {failed_names})"

    return ValuationOutput(
        asset_id=asset.asset_id,
        confirmed_total_valuation=confirmed_total_valuation,
        valuation_per_unit=closing_price_per_unit,
        methodology=methodology,
        effective_date=effective_date,
        tranche_values=tranche_values,
        prior_total_carrying_value=prior_total_carrying_value,
        valuation_uplift=valuation_uplift,
        validation_status=validation_status,
        validation_checks=checks,
        source_tool=source_tool,
    )
