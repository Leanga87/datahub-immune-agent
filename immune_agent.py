# immune_agent.py
# ImmuneAgent: detects the impact of a broken table, evaluates criticality,
# and raises an Incident in DataHub to halt downstream pipelines.

import sys
import requests
from datahub.sdk import DataHubClient

GMS_SERVER = "http://localhost:8080"
client = DataHubClient(server=GMS_SERVER)

broken_table = "urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.order_entry_db.order_entry.orders,PROD)"

# --- Find affected tables (downstream) ---
try:
    affected = client.lineage.get_lineage(
        source_urn=broken_table,
        direction="downstream",
        max_hops=1,
    )
except Exception as e:
    print(f"ERROR: could not query lineage from DataHub: {e}")
    sys.exit(1)

if len(affected) == 0:
    print("No downstream assets found. No incidents to create.")
    sys.exit(0)

print(f"Affected tables found: {len(affected)}\n")

for table in affected:
    affected_urn = table.urn

    try:
        dataset = client.entities.get(affected_urn)
    except Exception as e:
        print(f"ERROR: could not read table {affected_urn}: {e}")
        continue

    tag_names = []
    if dataset.tags:
        for tag_association in dataset.tags:
            clean_name = str(tag_association.tag).split(".")[-1]
            tag_names.append(clean_name)

    critical_keywords = ["authoritative", "most queried", "large table"]
    is_critical = any(
        keyword in tag.lower()
        for tag in tag_names
        for keyword in critical_keywords
    )

    severity = "HIGH" if is_critical else "MEDIUM"

    description = (
        f"Table affected by data corruption in 'orders'. "
        f"Tags detected: {tag_names}. Severity: {severity}."
    )

    print(f"Table: {affected_urn}")
    print(f"Severity: {severity}")
    print(f"Description: {description}\n")

    mutation = """
    mutation raiseIncident($resourceUrn: String!, $title: String!, $description: String!) {
      raiseIncident(input: {
        type: OPERATIONAL
        resourceUrn: $resourceUrn
        title: $title
        description: $description
      })
    }
    """

    variables = {
        "resourceUrn": affected_urn,
        "title": f"[{severity}] Corrupted data propagated from 'orders'",
        "description": description,
    }

    try:
        response = requests.post(
            f"{GMS_SERVER}/api/graphql",
            json={"query": mutation, "variables": variables},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR connecting to DataHub: {e}")
        continue

    if "errors" in result:
        print(f"ERROR from DataHub while creating the incident: {result['errors']}")
        continue

    print("Incident created successfully:", result["data"]["raiseIncident"])

