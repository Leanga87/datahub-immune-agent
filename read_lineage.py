# read_lineage.py
# Given the URN of a "broken" table, finds which tables depend on it (downstream).

from datahub.sdk import DataHubClient

client = DataHubClient(server="http://localhost:8080")

# URN of the table we simulate as broken (orders)
broken_table = "urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.order_entry_db.order_entry.orders,PROD)"

affected = client.lineage.get_lineage(
    source_urn=broken_table,
    direction="downstream",
    max_hops=1,
)

print(f"Tables affected by 'orders' breaking: {len(affected)}\n")

for table in affected:
    print(f"- Name: {table.name}")
    print(f"  URN: {table.urn}")
    print(f"  Platform: {table.platform}")
    print()

