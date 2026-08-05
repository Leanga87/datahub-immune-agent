# test_connection.py
# Prueba de conexión básica a la instancia local de DataHub.

from datahub.ingestion.graph.client import DataHubGraph, DatahubClientConfig

# Configuración del cliente: apunta al GMS (servidor) corriendo en Docker local
config = DatahubClientConfig(server="http://localhost:8080")
graph = DataHubGraph(config)

print("Conectado a DataHub correctamente!")

# Trae URNs (identificadores únicos) de entidades tipo "dataset" (tablas)
# get_urns_by_filter devuelve un generador, no una lista completa en memoria
resultados = graph.get_urns_by_filter(entity_types=["dataset"])

# Mostramos solo las primeras 5 para verificar que trajo datos reales
for i, urn in enumerate(resultados):
    if i >= 5:
        break
    print(urn)

