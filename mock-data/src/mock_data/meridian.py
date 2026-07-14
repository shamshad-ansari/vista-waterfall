"""Raw fixture data for the Meridian Software Group / AGF3-2018 demo scenario.

Transcribed verbatim from mock_datasets_Final_12pm.md SS1.1-1.3, SS2.1-2.2, SS2.7.
"""

from datetime import date

from mock_data.models import (
    AssetRecord,
    CashflowRecord,
    FundRules,
    LPCommitment,
    PriceFeedResponse,
    TrancheContribution,
    TrancheRecord,
)

ASSET_ID = "MSC-2019-047"
FUND_ID = "AGF3-2018"

ASSET_RECORD = AssetRecord(
    asset_id=ASSET_ID,
    asset_name="Meridian Software Group",
    asset_type="Private Equity — Direct Equity",
    sector="B2B SaaS",
    region="North America",
    fund_id=FUND_ID,
    fund_name="Acme Growth Fund III",
    initial_investment_date=date(2019, 3, 15),
    current_ownership_pct=1.00,
    prior_total_carrying_value=295_000_000,
    valuation_status="REVALUATION REQUIRED — new tranche closed",
    tranches=[
        TrancheRecord(
            tranche_id="MSC-T1",
            investment_date=date(2019, 3, 15),
            ownership_acquired_pct=0.45,
            cost_basis=58_500_000,
            security_type="Common Equity",
            units_held=4_500_000,
            cost_per_unit=13.00,
            prior_mark_per_unit=29.50,
            prior_carrying_value=132_750_000,
            last_valuation_date=date(2026, 3, 31),
            pricing_status="PRICED — prior quarterly cycle",
        ),
        TrancheRecord(
            tranche_id="MSC-T2",
            investment_date=date(2020, 8, 20),
            ownership_acquired_pct=0.25,
            cost_basis=47_500_000,
            security_type="Common Equity",
            units_held=2_500_000,
            cost_per_unit=19.00,
            prior_mark_per_unit=29.50,
            prior_carrying_value=73_750_000,
            last_valuation_date=date(2026, 3, 31),
            pricing_status="PRICED — prior quarterly cycle",
        ),
        TrancheRecord(
            tranche_id="MSC-T3",
            investment_date=date(2026, 6, 1),
            ownership_acquired_pct=0.30,
            cost_basis=102_000_000,
            security_type="Common Equity",
            units_held=3_000_000,
            closing_price_per_unit=34.00,
            pricing_status="AWAITING PRICE CONFIRMATION — customer price feed",
        ),
    ],
)

PRICE_FEED_RESPONSE = PriceFeedResponse(
    request_id="VAL-2026-0601-MSC",
    asset_id=ASSET_ID,
    tranche_id="MSC-T3",
    transaction_type="minority_buyout_close",
    closing_price_per_unit=34.00,
    units_transacted=3_000_000,
    total_transaction_value=102_000_000,
    transaction_date=date(2026, 6, 1),
    counterparty="Meridian founders & early employees (sellers)",
    methodology="negotiated_transaction_price",
    ic_approved_by="Investment Committee — 2026-05-28",
    arm_length_confirmation=True,
)

FUND_RULES = FundRules(
    fund_id=FUND_ID,
    fund_name="Acme Growth Fund III",
    waterfall_type="American — Deal-by-Deal",
    hurdle_rate=0.08,
    catch_up_structure="100% GP catch-up to 20% of total profit",
    carry_split_lp=0.80,
    carry_split_gp=0.20,
    gp_commitment_pct=0.02,
    total_commitments=450_000_000,
    clawback_provision="Yes — 3-year lookback",
    management_fee="2% during investment period",
)

LP_ROSTER = [
    LPCommitment(lp_id="LP-001", commitment_amount=75_000_000, ownership_pct=0.16667),
    LPCommitment(lp_id="LP-002", commitment_amount=50_000_000, ownership_pct=0.11111),
    LPCommitment(lp_id="LP-003", commitment_amount=100_000_000, ownership_pct=0.22222),
    LPCommitment(lp_id="LP-004", commitment_amount=25_000_000, ownership_pct=0.05556),
    LPCommitment(lp_id="LP-005", commitment_amount=50_000_000, ownership_pct=0.11111),
    LPCommitment(lp_id="LP-006", commitment_amount=30_000_000, ownership_pct=0.06667),
    LPCommitment(lp_id="LP-007", commitment_amount=25_000_000, ownership_pct=0.05556),
    LPCommitment(lp_id="LP-008", commitment_amount=40_000_000, ownership_pct=0.08889),
    LPCommitment(lp_id="LP-009", commitment_amount=30_000_000, ownership_pct=0.06667),
    LPCommitment(lp_id="LP-010", commitment_amount=25_000_000, ownership_pct=0.05556),
]

CASHFLOW_RECORD = CashflowRecord(
    investment_id=ASSET_ID,
    contributed_capital_total=208_000_000,
    contributions=[
        TrancheContribution(tranche_id="MSC-T1", amount=58_500_000, date=date(2019, 3, 15)),
        TrancheContribution(tranche_id="MSC-T2", amount=47_500_000, date=date(2020, 8, 20)),
        TrancheContribution(tranche_id="MSC-T3", amount=102_000_000, date=date(2026, 6, 1)),
    ],
    prior_distributions_this_investment=0,
    realization_date=date(2026, 6, 1),
)
