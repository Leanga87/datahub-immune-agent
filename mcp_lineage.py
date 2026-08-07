# mcp_lineage.py
# Uses the DataHub MCP Server (Model Context Protocol) to fetch downstream
# lineage for a broken table — the same lineage lookup as read_lineage.py,
# but through the official MCP Server instead of the direct SDK call.

import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BROKEN_TABLE = "urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.order_entry_db.order_entry.orders,PROD)"


async def main():
    server_params = StdioServerParameters(
        command="mcp-server-datahub",
        args=[],
        env={**os.environ, "DATAHUB_GMS_URL": "http://localhost:8080"},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "get_lineage",
                arguments={
                    "urn": BROKEN_TABLE,
                    "upstream": False,
                    "max_hops": 1,
                },
            )

            print("Downstream lineage (via DataHub MCP Server):\n")
            for content in result.content:
                print(content.text)


if __name__ == "__main__":
    asyncio.run(main())

