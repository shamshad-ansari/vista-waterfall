import json
from datetime import date

from valuation_mcp.reasoning import value_asset
from valuation_mcp.schemas.valuation import ValuationInput

DEFAULT_ASSET_ID = "MSC-2019-047"


def register_valuation_tools(mcp) -> None:
    """Register valuation tools on the FastMCP instance."""

    @mcp.tool(
        name="valuation_get_asset_valuation",
        annotations={
            "title": "Get Asset Valuation",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def valuation_get_asset_valuation(
        asset_id: str = DEFAULT_ASSET_ID,
        closing_price_per_unit: float | None = None,
        methodology: str | None = None,
        ic_approved_by: str | None = None,
        effective_date: date | None = None,
        arm_length_confirmation: bool | None = None,
    ) -> str:
        """Return a confirmed asset valuation from the ledger record and a new tranche's closing price.

        Loads the asset + its tranches via the native Ledger Data Tool stand-in
        (mock_data.get_asset_record), derives the implied enterprise value from
        the newly priced tranche's closing price, restates the other tranches
        against it, runs the standard validation checks, and returns the
        confirmed valuation.

        Use when: an agent needs a confirmed asset valuation after a new
        tranche closes.
        Do NOT use when: no tranche is awaiting a price (nothing to revalue).

        Args:
            asset_id: Asset identifier to load from the ledger.
            closing_price_per_unit: New closing/transaction price per unit for
                the unpriced tranche, as returned by the customer's registered
                Price Feed Tool. If omitted, falls back to
                mock_data.get_price_feed_response as the demo stand-in for
                that external call.
            methodology: Pricing methodology used (Price Feed Tool field).
            ic_approved_by: Investment Committee approval reference.
            effective_date: Date the new price became effective.
            arm_length_confirmation: Whether the transaction was arm's-length.

        Returns:
            JSON string matching ValuationOutput schema.
        """
        payload = ValuationInput(
            asset_id=asset_id,
            closing_price_per_unit=closing_price_per_unit,
            methodology=methodology,
            ic_approved_by=ic_approved_by,
            effective_date=effective_date,
            arm_length_confirmation=arm_length_confirmation,
        )
        result = value_asset(payload)
        return json.dumps(result.model_dump(mode="json"), indent=2)

