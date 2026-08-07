# ImmuneAgent

AI agent that reads DataHub lineage, evaluates data-quality risk using
governance tags, and autonomously raises incidents to halt downstream
pipelines before corrupted data spreads.

## Problem

When an upstream table gets corrupted, traditional pipelines keep processing
downstream data blindly. By the time someone notices, bad data has already
reached dashboards and reports.

## Solution

ImmuneAgent detects the impact automatically:

orders (corrupted) --> lineage lookup --> order_details (downstream)
|
evaluate criticality (tags)
|
raise Incident in DataHub
|

Unlike a fixed rule, the agent reasons about severity using the table's
own governance signals (e.g. "Authoritative Source", "Most Queried") before
deciding whether to raise a high-priority incident.

## How it works

1. `read_lineage.py` — reads downstream lineage from a given dataset.
2. `evaluate_criticality.py` — reads tags and decides severity.
3. `immune_agent.py` — combines both steps and raises a real Incident in
   DataHub via GraphQL.
4. `pipeline_check.py` — simulates a pipeline step that checks for
   active incidents before processing, and halts if one is found.
5. `mcp_lineage.py` — demonstrates the same downstream lineage lookup 
   performed through the official DataHub MCP Server (Model Context 
   Protocol), confirming compatibility with MCP-based agent workflows.

## Setup

Requirements: Python 3.11, Docker Desktop, WSL2 (on Windows).

```bash
# 1. Start DataHub locally
pip install acryl-datahub
datahub docker quickstart

# 2. Load sample e-commerce data
datahub init
datahub datapack load showcase-ecommerce

# 3. Install project dependencies
python3.11 -m venv venv
source venv/bin/activate
pip install acryl-datahub requests

# 4. Run the full flow
# 4. Run the full flow
python immune_agent.py       # detects, reasons, raises incident
python pipeline_check.py     # confirms the pipeline halts
```

## Known Limitations

This demo uses the local DataHub Quickstart deployment. Authentication is
intentionally disabled, since the focus of this project is the autonomous
reasoning and incident-generation logic, not production deployment
hardening.

## License

Apache 2.0



