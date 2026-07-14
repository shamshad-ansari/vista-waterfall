import json

from valuation_mcp.schemas.valuation import ValuationOutput

# Hardcoded scaffold values — replace with real pricing/valuation logic later.
HARDCODED_CLOSING_PRICE = 125.50
HARDCODED_ASSET_VALUATION = 1_250_000.00
HARDCODED_POSITION_ID = "POS-001"


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
    async def valuation_get_asset_valuation() -> str:
        """Return the valuation of an asset from a position closing price.

        Use when: an agent needs the current asset valuation for a held position.
        Do NOT use when: live market data or user-supplied prices are required
        (scaffold returns hardcoded demo values only).

        Returns:
            JSON string matching ValuationOutput schema.
        """
        result = ValuationOutput(
            position_id=HARDCODED_POSITION_ID,
            closing_price=HARDCODED_CLOSING_PRICE,
            asset_valuation=HARDCODED_ASSET_VALUATION,
            currency="USD",
            valuation_method="hardcoded_scaffold",
        )
        return json.dumps(result.model_dump(), indent=2)
