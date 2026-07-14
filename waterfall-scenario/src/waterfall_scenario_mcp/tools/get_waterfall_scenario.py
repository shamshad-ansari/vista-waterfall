import json

from peak_contracts.models.waterfall_model import (
    WaterfallLpDistribution,
    WaterfallModelInput,
    WaterfallModelOutput,
)

# Hardcoded scaffold values — replace with real waterfall engine later.
HARDCODED_ASSET_VALUATION = 1_250_000.00
HARDCODED_LP_DISTRIBUTIONS = [
    WaterfallLpDistribution(
        lp_id="LP-001",
        lp_name="Institutional A",
        lp_class="Class A",
        distribution_amount=500_000.00,
    ),
    WaterfallLpDistribution(
        lp_id="LP-002",
        lp_name="Institutional B",
        lp_class="Class B",
        distribution_amount=375_000.00,
    ),
    WaterfallLpDistribution(
        lp_id="LP-003",
        lp_name="Family Office C",
        lp_class="Class A",
        distribution_amount=250_000.00,
    ),
    WaterfallLpDistribution(
        lp_id="GP-001",
        lp_name="General Partner",
        lp_class="Carried Interest",
        distribution_amount=125_000.00,
    ),
]


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
        asset_valuation: float = HARDCODED_ASSET_VALUATION,
        fund_id: str = "FUND-001",
    ) -> str:
        """Return a waterfall scenario allocating an asset valuation across LPs.

        Implements the `waterfall-model` override contract. Use when a firm's own
        waterfall engine should replace the native Peak engine for LP splits.

        Scaffold: returns hardcoded demo distributions regardless of input.

        Returns:
            JSON string matching WaterfallModelOutput schema.
        """
        payload = WaterfallModelInput(asset_valuation=asset_valuation, fund_id=fund_id)
        result = WaterfallModelOutput(
            fund_id=payload.fund_id,
            asset_valuation=payload.asset_valuation,
            currency="USD",
            waterfall_method="hardcoded_scaffold",
            lp_distributions=HARDCODED_LP_DISTRIBUTIONS,
            total_distributed=sum(d.distribution_amount for d in HARDCODED_LP_DISTRIBUTIONS),
        )
        return json.dumps(result.model_dump(by_alias=True), indent=2)
