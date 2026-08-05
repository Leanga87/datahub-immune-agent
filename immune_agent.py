# immune_agent.py
# ImmuneAgent: detecta el impacto de una tabla rota, evalúa criticidad
# y levanta un Incident en DataHub para frenar pipelines downstream.

import sys
import requests
from datahub.sdk import DataHubClient

GMS_SERVER = "http://localhost:8080"
client = DataHubClient(server=GMS_SERVER)

tabla_rota = "urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.order_entry_db.order_entry.orders,PROD)"

# --- Encontrar tablas afectadas (downstream) ---
try:
    afectadas = client.lineage.get_lineage(
        source_urn=tabla_rota,
        direction="downstream",
        max_hops=1,
    )
except Exception as e:
    print(f"ERROR: no se pudo consultar el linaje en DataHub: {e}")
    sys.exit(1)

if len(afectadas) == 0:
    print("No se encontraron tablas afectadas (downstream). No hay incidentes que crear.")
    sys.exit(0)

print(f"Tablas afectadas encontradas: {len(afectadas)}\n")

for tabla in afectadas:
    urn_afectada = tabla.urn

    try:
        dataset = client.entities.get(urn_afectada)
    except Exception as e:
        print(f"ERROR: no se pudo leer la tabla {urn_afectada}: {e}")
        continue  # seguimos con la siguiente tabla afectada, si hay más

    nombres_tags = []
    if dataset.tags:
        for tag_asociado in dataset.tags:
            nombre_limpio = str(tag_asociado.tag).split(".")[-1]
            nombres_tags.append(nombre_limpio)

    palabras_criticas = ["authoritative", "most queried", "large table"]
    es_critica = any(
        palabra in tag.lower()
        for tag in nombres_tags
        for palabra in palabras_criticas
    )

    severidad_texto = "ALTA" if es_critica else "MEDIA"

    descripcion = (
        f"Tabla afectada por corrupción de datos en 'orders'. "
        f"Tags detectados: {nombres_tags}. Severidad: {severidad_texto}."
    )

    print(f"Tabla: {urn_afectada}")
    print(f"Severidad: {severidad_texto}")
    print(f"Descripción: {descripcion}\n")

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
        "resourceUrn": urn_afectada,
        "title": f"[{severidad_texto}] Datos corruptos propagados desde 'orders'",
        "description": descripcion,
    }

    try:
        respuesta = requests.post(
            f"{GMS_SERVER}/api/graphql",
            json={"query": mutation, "variables": variables},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        respuesta.raise_for_status()
        resultado = respuesta.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR conectando con DataHub: {e}")
        continue

    if "errors" in resultado:
        print(f"ERROR de DataHub al crear el incidente: {resultado['errors']}")
        continue

    print("Incidente creado con éxito:", resultado["data"]["raiseIncident"])

