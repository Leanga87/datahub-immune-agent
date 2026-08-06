# pipeline_check.py
# Simulates a pipeline step that, before processing a table,
# checks DataHub for active incidents and halts if any are found.

import sys
import requests

GMS_SERVER = "http://localhost:8080"

table_to_process = "urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.ORDER_ENTRY_DB.analytics.order_details,PROD)"

query = """
query getAssetIncidents($urn: String!) {
  dataset(urn: $urn) {
    incidents(state: ACTIVE, start: 0, count: 20) {
      total
      incidents {
        title
        status {
          state
        }
      }
    }
  }
}
"""

variables = {"urn": table_to_process}

print("Starting processing of 'order_details'...")

try:
    response = requests.post(
        f"{GMS_SERVER}/api/graphql",
        json={"query": query, "variables": variables},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    result = response.json()
except requests.exceptions.RequestException as e:
    print(f"ERROR connecting to DataHub: {e}")
    sys.exit(1)

if "errors" in result:
    print(f"ERROR from DataHub while checking incidents: {result['errors']}")
    sys.exit(1)

incidents = result["data"]["dataset"]["incidents"]

print(f"Active incidents found: {incidents['total']}\n")

if incidents["total"] > 0:
    print("🛑 PIPELINE HALTED — the table has active incidents:")
    for inc in incidents["incidents"]:
        print(f"  - {inc['title']}")
    print("\nProcessing will not continue until the incident is resolved.")
else:
    print("✅ No active incidents. Processing table normally...")

