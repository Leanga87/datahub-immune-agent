# evaluar_criticidad.py
# Lee los tags de la tabla afectada y decide qué tan grave es el incidente.

from datahub.sdk import DataHubClient, DatasetUrn

client = DataHubClient(server="http://localhost:8080")

# URN de la tabla afectada (la encontramos en read_lineage.py)
tabla_afectada = DatasetUrn(
    platform="dbt",
    name="b2fd91.ORDER_ENTRY_DB.analytics.order_details",
    env="PROD",
)

# Traemos la entidad completa desde DataHub (incluye sus tags)
dataset = client.entities.get(tabla_afectada)

# Cada tag viene como un objeto con el URN completo (ej: "urn:li:tag:b2fd91.Authoritative Source")
# Nos quedamos solo con el nombre legible, después del último punto
nombres_tags = []
if dataset.tags:
    for tag_asociado in dataset.tags:
        urn_completo = str(tag_asociado.tag)
        nombre_limpio = urn_completo.split(".")[-1]
        nombres_tags.append(nombre_limpio)

print(f"Tags encontrados en la tabla: {nombres_tags}\n")

# Palabras clave que consideramos "críticas" para decidir la severidad
palabras_criticas = ["authoritative", "most queried", "large table"]

es_critica = any(
    palabra in tag.lower()
    for tag in nombres_tags
    for palabra in palabras_criticas
)

if es_critica:
    severidad = "ALTA"
    motivo = (
        "La tabla 'order_details' depende de 'orders', que fue marcada como "
        "corrupta. 'order_details' está etiquetada como tabla autoritativa y "
        "muy consultada, por lo que el impacto de datos incorrectos es alto."
    )
else:
    severidad = "BAJA"
    motivo = (
        "La tabla 'order_details' depende de 'orders', que fue marcada como "
        "corrupta, pero no tiene etiquetas que indiquen uso crítico."
    )

print(f"Severidad decidida: {severidad}")
print(f"Motivo: {motivo}")

