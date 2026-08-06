# evaluate_criticality.py
# Reads the tags of the affected table and decides how severe the incident is.

from datahub.sdk import DataHubClient, DatasetUrn

client = DataHubClient(server="http://localhost:8080")

# URN of the affected table (found in read_lineage.py)
affected_table = DatasetUrn(
    platform="dbt",
    name="b2fd91.ORDER_ENTRY_DB.analytics.order_details",
    env="PROD",
)

dataset = client.entities.get(affected_table)

# Each tag comes as an object with the full URN (e.g. "urn:li:tag:b2fd91.Authoritative Source")
# We keep only the readable name, after the last dot
tag_names = []
if dataset.tags:
    for tag_association in dataset.tags:
        full_urn = str(tag_association.tag)
        clean_name = full_urn.split(".")[-1]
        tag_names.append(clean_name)

print(f"Tags found on the table: {tag_names}\n")

# Keywords we consider "critical" when deciding severity
critical_keywords = ["authoritative", "most queried", "large table"]

is_critical = any(
    keyword in tag.lower()
    for tag in tag_names
    for keyword in critical_keywords
)

if is_critical:
    severity = "HIGH"
    reason = (
        "Table 'order_details' depends on 'orders', which was flagged as "
        "corrupted. 'order_details' is tagged as an authoritative and "
        "heavily queried table, so the impact of incorrect data is high."
    )
else:
    severity = "LOW"
    reason = (
        "Table 'order_details' depends on 'orders', which was flagged as "
        "corrupted, but has no tags indicating critical usage."
    )

print(f"Severity decided: {severity}")
print(f"Reason: {reason}")

