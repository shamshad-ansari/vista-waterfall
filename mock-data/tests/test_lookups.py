import pytest

from mock_data.lookups import (
    UnknownAssetError,
    UnknownFundError,
    UnknownInvestmentError,
    UnknownTrancheError,
    get_asset_record,
    get_cashflows,
    get_fund_rules,
    get_lp_roster,
    get_price_feed_response,
)

ASSET_ID = "MSC-2019-047"
FUND_ID = "AGF3-2018"


def test_get_asset_record_known_id():
    record = get_asset_record(ASSET_ID)

    assert record.asset_id == ASSET_ID
    assert record.asset_name == "Meridian Software Group"
    assert len(record.tranches) == 3
    assert record.tranches[0].tranche_id == "MSC-T1"
    assert record.tranches[0].cost_basis == 58_500_000
    assert record.tranches[2].units_held == 3_000_000
    assert record.tranches[2].closing_price_per_unit == 34.00


def test_get_asset_record_unknown_id_raises():
    with pytest.raises(UnknownAssetError):
        get_asset_record("NOT-A-REAL-ASSET")


def test_get_price_feed_response_known_ids():
    response = get_price_feed_response(ASSET_ID, "MSC-T3")

    assert response.asset_id == ASSET_ID
    assert response.tranche_id == "MSC-T3"
    assert response.closing_price_per_unit == 34.00
    assert response.units_transacted == 3_000_000
    assert response.arm_length_confirmation is True


def test_get_price_feed_response_unknown_asset_raises():
    with pytest.raises(UnknownAssetError):
        get_price_feed_response("NOT-A-REAL-ASSET", "MSC-T3")


def test_get_price_feed_response_unknown_tranche_raises():
    with pytest.raises(UnknownTrancheError):
        get_price_feed_response(ASSET_ID, "MSC-T99")


def test_get_fund_rules_known_id():
    rules = get_fund_rules(FUND_ID)

    assert rules.fund_id == FUND_ID
    assert rules.hurdle_rate == 0.08
    assert rules.carry_split_lp == 0.80
    assert rules.carry_split_gp == 0.20
    assert rules.waterfall_type == "American — Deal-by-Deal"


def test_get_fund_rules_unknown_id_raises():
    with pytest.raises(UnknownFundError):
        get_fund_rules("NOT-A-REAL-FUND")


def test_get_lp_roster_known_id():
    roster = get_lp_roster(FUND_ID)

    assert len(roster) == 10
    assert sum(lp.commitment_amount for lp in roster) == 450_000_000
    lp_003 = next(lp for lp in roster if lp.lp_id == "LP-003")
    assert lp_003.commitment_amount == 100_000_000


def test_get_lp_roster_unknown_id_raises():
    with pytest.raises(UnknownFundError):
        get_lp_roster("NOT-A-REAL-FUND")


def test_get_cashflows_known_id():
    cashflows = get_cashflows(ASSET_ID)

    assert cashflows.investment_id == ASSET_ID
    assert cashflows.contributed_capital_total == 208_000_000
    assert len(cashflows.contributions) == 3
    assert cashflows.prior_distributions_this_investment == 0
    assert not hasattr(cashflows, "distributable_cash")


def test_get_cashflows_unknown_id_raises():
    with pytest.raises(UnknownInvestmentError):
        get_cashflows("NOT-A-REAL-INVESTMENT")
