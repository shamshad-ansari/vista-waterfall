import json
import sys

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

GATEWAY_COMMAND = str((sys.exec_prefix and f"{sys.exec_prefix}/bin/mcp-gateway"))


@pytest.mark.asyncio
async def test_gateway_aggregates_both_backend_tools():
    params = StdioServerParameters(command=GATEWAY_COMMAND, args=[])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}

    assert names == {
        "valuation_get_asset_valuation",
        "waterfall_scenario_compute_lp_distributions",
    }


@pytest.mark.asyncio
async def test_gateway_forwards_meridian_golden_path():
    params = StdioServerParameters(command=GATEWAY_COMMAND, args=[])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            val_result = await session.call_tool(
                "valuation_get_asset_valuation", {"asset_id": "MSC-2019-047"}
            )
            valuation = json.loads(val_result.content[0].text)
            assert valuation["confirmed_total_valuation"] == 340_000_000

            wf_result = await session.call_tool(
                "waterfall_scenario_compute_lp_distributions",
                {
                    "investment_id": "MSC-2019-047",
                    "fund_id": "AGF3-2018",
                    "distributable_cash": valuation["confirmed_total_valuation"],
                },
            )
            scenario = json.loads(wf_result.content[0].text)

    assert scenario["lp_total"] == 313_600_000
    assert scenario["gp_total"] == 26_400_000
