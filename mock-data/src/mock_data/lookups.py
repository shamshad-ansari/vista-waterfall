from mock_data.meridian import (
    ASSET_ID,
    ASSET_RECORD,
    CASHFLOW_RECORD,
    FUND_ID,
    FUND_RULES,
    LP_ROSTER,
    PRICE_FEED_RESPONSE,
)
from mock_data.models import AssetRecord, CashflowRecord, FundRules, LPCommitment, PriceFeedResponse


class UnknownAssetError(ValueError):
    """Raised when the requested asset_id isn't the Meridian demo scenario."""


class UnknownFundError(ValueError):
    """Raised when the requested fund_id isn't the AGF3-2018 demo scenario."""


class UnknownInvestmentError(ValueError):
    """Raised when the requested investment_id isn't the Meridian demo scenario."""


class UnknownTrancheError(ValueError):
    """Raised when the requested tranche_id isn't one of Meridian's tranches."""


def get_asset_record(asset_id: str) -> AssetRecord:
    if asset_id != ASSET_ID:
        raise UnknownAssetError(f"No asset record for asset_id '{asset_id}'")
    return ASSET_RECORD


def get_price_feed_response(asset_id: str, tranche_id: str) -> PriceFeedResponse:
    if asset_id != ASSET_ID:
        raise UnknownAssetError(f"No price feed response for asset_id '{asset_id}'")
    if tranche_id != PRICE_FEED_RESPONSE.tranche_id:
        raise UnknownTrancheError(f"No price feed response for tranche_id '{tranche_id}'")
    return PRICE_FEED_RESPONSE


def get_fund_rules(fund_id: str) -> FundRules:
    if fund_id != FUND_ID:
        raise UnknownFundError(f"No fund rules for fund_id '{fund_id}'")
    return FUND_RULES


def get_lp_roster(fund_id: str) -> list[LPCommitment]:
    if fund_id != FUND_ID:
        raise UnknownFundError(f"No LP roster for fund_id '{fund_id}'")
    return LP_ROSTER


def get_cashflows(investment_id: str) -> CashflowRecord:
    if investment_id != ASSET_ID:
        raise UnknownInvestmentError(f"No cashflow record for investment_id '{investment_id}'")
    return CASHFLOW_RECORD
