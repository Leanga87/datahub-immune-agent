# read_lineage.py
# Dado el URN de una tabla "rota", encuentra qué tablas dependen de ella (downstream).

from datahub.sdk import DataHubClient

client = DataHubClient(server="http://localhost:8080")

# URN de la tabla que simulamos que se rompió (orders)
tabla_rota = "urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.order_entry_db.order_entry.orders,PROD)"

# Pedimos las entidades downstream (que dependen de tabla_rota), 1 salto de distancia
afectadas = client.lineage.get_lineage(
    source_urn=tabla_rota,
    direction="downstream",
    max_hops=1,
)

print(f"Tablas afectadas por la ruptura de 'orders': {len(afectadas)}\n")

for tabla in afectadas:
    print(f"- Nombre: {tabla.name}")
    print(f"  URN: {tabla.urn}")
    print(f"  Plataforma: {tabla.platform}")
    print()

