# Validación del dataset — MCDI500

**Archivo:** `incidencias_alumbrado_2025_2026.csv` · 10000 filas × 19 columnas

## Perfil de variables

| variable | dtype | rol | unicos | pct_nulos |
| --- | --- | --- | --- | --- |
| unique_key | int64 | identificador | 10000 | 0.0 |
| created_date | str | fecha | 9085 | 0.0 |
| closed_date | str | fecha | 4754 | 33.9 |
| resolution_action_updated_date | str | fecha | 5032 | 27.5 |
| agency | str | nominal | 1 | 0.0 |
| agency_name | str | nominal | 1 | 0.0 |
| complaint_type | str | nominal | 1 | 0.0 |
| descriptor | str | alta cardinalidad | 40 | 0.0 |
| status | str | nominal | 4 | 0.0 |
| resolution_description | str | binaria | 2 | 27.5 |
| borough | str | nominal | 6 | 0.0 |
| community_board | str | alta cardinalidad | 73 | 0.0 |
| city | str | alta cardinalidad | 42 | 3.4 |
| incident_zip | float64 | discreta | 185 | 3.5 |
| latitude | float64 | continua | 7275 | 5.8 |
| longitude | float64 | continua | 7275 | 5.8 |
| open_data_channel_type | str | nominal | 1 | 0.0 |
| council_district | float64 | discreta | 51 | 6.0 |
| police_precinct | str | alta cardinalidad | 78 | 0.0 |

## Requisitos del curso

| estado | requisito | detalle |
| --- | --- | --- |
| OK | Al menos 2000 filas | 10000 filas |
| OK | Al menos 12 columnas | 19 columnas |
| OK | Combina al menos 3 roles analíticos | nominal, alta cardinalidad, fecha, discreta, continua, binaria |
| OK | Al menos una variable numérica | 4 numéricas (continuas o discretas) |
| OK | Al menos una variable categórica | 7 categóricas (nominales, binarias u ordinales) |
| OK | Presencia de valores faltantes | máximo 33.9% en una variable |
| OK | Ninguna variable sobre 60% de faltantes | máximo 33.9% |
| OK | Incluye alguna variable de fecha | 3 detectadas |
| OK | Incluye texto o categórica de alta cardinalidad | 4 detectadas |
| OK | Archivo bajo 100 MB | 3.4 MB |
| OK | Sin filas duplicadas exactas | ninguna |

## Resultado

El conjunto **cumple** los requisitos mínimos.