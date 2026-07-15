"""Static backend registry for the aggregating gateway.

Static, not dynamically discovered: with two domain servers today (and a
handful expected for this project), a hand-maintained list is simpler and
more debuggable than a registration protocol. See docs/adr/008.

Each backend is launched as a local stdio subprocess, the same console
script Claude Desktop launches directly today (see issue 007) — the gateway
just launches both instead of Claude launching each separately, and mounts
their tools under one connection.
"""

import sys
from pathlib import Path

# Console scripts for both domain servers are installed into the same venv
# as this gateway (single shared .venv, no root workspace tool — see repo
# root). Resolve them relative to the running interpreter rather than
# relying on PATH, so this works regardless of the launching process's cwd
# or environment (e.g. Claude Desktop's subprocess launch).
_VENV_BIN = Path(sys.executable).parent

BACKENDS: dict[str, dict] = {
    "valuation_mcp": {
        "command": str(_VENV_BIN / "valuation-mcp"),
        "args": [],
    },
    "waterfall_scenario_mcp": {
        "command": str(_VENV_BIN / "waterfall-scenario-mcp"),
        "args": [],
    },
}
