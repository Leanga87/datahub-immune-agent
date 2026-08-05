# pipeline_simulado.py
# Simula un paso de un pipeline que, antes de procesar una tabla,
# consulta si tiene incidentes activos en DataHub y se frena si los tiene.

import sys
import requests

GMS_SERVER = "http://localhost:8080"

tabla_a_procesar = "urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.ORDER_ENTRY_DB.analytics.order_details,PROD)"

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

variables = {"urn": tabla_a_procesar}

print("Iniciando procesamiento de 'order_details'...")

try:
    respuesta = requests.post(
        f"{GMS_SERVER}/api/graphql",
        json={"query": query, "variables": variables},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    respuesta.raise_for_status()
    resultado = respuesta.json()
except requests.exceptions.RequestException as e:
    print(f"ERROR conectando con DataHub: {e}")
    sys.exit(1)

if "errors" in resultado:
    print(f"ERROR de DataHub al consultar incidentes: {resultado['errors']}")
    sys.exit(1)

incidentes = resultado["data"]["dataset"]["incidents"]

print(f"Incidentes activos encontrados: {incidentes['total']}\n")

if incidentes["total"] > 0:
    print("🛑 PIPELINE DETENIDO — la tabla tiene incidentes activos:")
    for inc in incidentes["incidents"]:
        print(f"  - {inc['title']}")
    print("\nEl procesamiento no continuará hasta resolver el incidente.")
else:
    print("✅ Sin incidentes activos. Procesando tabla normalmente...")

