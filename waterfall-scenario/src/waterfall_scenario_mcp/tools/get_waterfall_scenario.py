import json

from waterfall_scenario_mcp.reasoning import compute_waterfall_scenario
from waterfall_scenario_mcp.schemas.waterfall import WaterfallInput

DEFAULT_INVESTMENT_ID = "MSC-2019-047"
DEFAULT_FUND_ID = "AGF3-2018"


def register_waterfall_scenario_tools(mcp) -> None:
    """Register waterfall scenario tools on the FastMCP instance."""

    @mcp.tool(
        name="waterfall_scenario_compute_lp_distributions",
        annotations={
            "title": "Compute LP Waterfall Distributions",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def waterfall_scenario_compute_lp_distributions(
        distributable_cash: float,
        investment_id: str = DEFAULT_INVESTMENT_ID,
        fund_id: str = DEFAULT_FUND_ID,
    ) -> str:
        """Return a draft waterfall distribution scenario from a confirmed exit valuation.

        Loads fund rules and the LP roster via the native Fund & Investor
        Static Tool stand-in (mock_data.get_fund_rules / mock_data.get_lp_roster)
        and the investment's cashflow tranches via the native Accounting
        Cashflows Tool stand-in (mock_data.get_cashflows), runs the pooled
        American/deal-by-deal tier sequence (return of capital, preferred
        return, GP catch-up, residual split), then splits the resulting
        LP-tier-total across the LP roster pro-rata by fund commitment %.

        Use when: the Valuation Agent has confirmed an exit valuation and the
        orchestrator needs a draft distribution scenario for GP HITL review.
        Do NOT use when: the valuation hasn't been confirmed yet.

        Args:
            distributable_cash: Confirmed exit valuation for this realization
                event — the Valuation Agent's confirmed_total_valuation.
            investment_id: Investment identifier to look up cashflow tranches for.
            fund_id: Fund identifier to look up fund rules and the LP roster for.

        Returns:
            JSON string matching WaterfallOutput schema. `status` is always
            "PENDING_HITL_APPROVAL" — treat this as a proposed distribution,
            not an approved one.
        """
        payload = WaterfallInput(
            investment_id=investment_id,
            fund_id=fund_id,
            distributable_cash=distributable_cash,
        )
        result = compute_waterfall_scenario(payload)
        return json.dumps(result.model_dump(mode="json"), indent=2)
