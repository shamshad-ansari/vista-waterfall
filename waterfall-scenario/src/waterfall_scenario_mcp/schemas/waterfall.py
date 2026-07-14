"""Waterfall schemas.

Source of truth is the frozen contract in ``peak_contracts``; this module
re-exports those models so the reference override MCP and the contract stay
in lockstep.
"""

from peak_contracts.models.waterfall_model import (
    WaterfallLpDistribution as LPDistribution,
    WaterfallModelInput as WaterfallInput,
    WaterfallModelOutput as WaterfallOutput,
)

__all__ = ["LPDistribution", "WaterfallInput", "WaterfallOutput"]
