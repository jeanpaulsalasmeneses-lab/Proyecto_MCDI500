# Validación del dataset — MCDI500

**Archivo:** `cen_fallas_2024_2026_eventos.csv` · 18019 filas × 40 columnas

## Perfil de variables

| variable | dtype | rol | unicos | pct_nulos |
| --- | --- | --- | --- | --- |
| ﻿Número | float64 | identificador | 18019 | 0.0 |
| Tipo | str | nominal | 3 | 0.0 |
| Estado | str | nominal | 3 | 0.0 |
| Empresa | str | alta cardinalidad | 423 | 0.0 |
| Id Coordinado | float64 | discreta | 347 | 1.6 |
| Origen | str | binaria | 2 | 0.0 |
| SubEstación | str | alta cardinalidad | 923 | 50.8 |
| Elemento(s) | str | alta cardinalidad | 3255 | 63.6 |
| Zona Afectada | str | alta cardinalidad | 43 | 6.1 |
| Comuna | str | alta cardinalidad | 1229 | 6.4 |
| Tipo Causa | str | binaria | 2 | 0.0 |
| Causa | str | binaria | 2 | 0.0 |
| Causa Definitiva | str | alta cardinalidad | 49 | 11.9 |
| Causa Fenomeno Físico | str | alta cardinalidad | 6591 | 7.2 |
| Causa Elementos | str | alta cardinalidad | 6715 | 7.3 |
| Causa Fenomeno Eléctrico | str | alta cardinalidad | 6318 | 8.1 |
| Causa Modo | str | nominal | 12 | 1.6 |
| Observaciones | str | texto libre | 11868 | 0.3 |
| Acciones Inmediatas | str | texto libre | 8919 | 0.3 |
| Hechos Sucedidos | str | texto libre | 11435 | 0.3 |
| Acciones Correctivas a Corto Plazo | str | alta cardinalidad | 4621 | 2.5 |
| Acciones Correctivas a Largo Plazo | str | alta cardinalidad | 2444 | 4.3 |
| Consumo | str | nominal | 4 | 1.6 |
| Distribuidoras Afectadas | str | alta cardinalidad | 492 | 62.2 |
| Fecha Perturbación | str | fecha | 9155 | 0.0 |
| Fechas Estimada Retorno | str | fecha | 12598 | 0.0 |
| Fecha Efectiva Fin | str | fecha | 9191 | 40.0 |
| Retorno Automático Falla | str | nominal | 6 | 1.6 |
| anio_publicacion | int64 | discreta | 3 | 0.0 |
| mes_publicacion | int64 | discreta | 12 | 0.0 |
| archivo_zip | str | alta cardinalidad | 33 | 0.0 |
| archivo_csv | str | alta cardinalidad | 33 | 0.0 |
| fila_fuente | int64 | continua | 1381 | 0.0 |
| id_falla | int64 | identificador | 18019 | 0.0 |
| anio_evento | int64 | discreta | 6 | 0.0 |
| mes_evento | int64 | discreta | 12 | 0.0 |
| intervalo_negativo | bool | nominal | 1 | 0.0 |
| duracion_horas | float64 | continua | 1376 | 40.0 |
| fecha_invalida_o_ausente | bool | nominal | 1 | 0.0 |
| fuera_de_periodo | bool | binaria | 2 | 0.0 |

## Requisitos del curso

| estado | requisito | detalle |
| --- | --- | --- |
| OK | Al menos 2000 filas | 18019 filas |
| OK | Al menos 12 columnas | 40 columnas |
| OK | Combina al menos 3 roles analíticos | alta cardinalidad, nominal, discreta, binaria, texto libre, fecha, continua |
| OK | Al menos una variable numérica | 7 numéricas (continuas o discretas) |
| OK | Al menos una variable categórica | 11 categóricas (nominales, binarias u ordinales) |
| OK | Presencia de valores faltantes | máximo 63.6% en una variable |
| AVISO | Ninguna variable sobre 60% de faltantes | máximo 63.6% |
| OK | Incluye alguna variable de fecha | 3 detectadas |
| OK | Incluye texto o categórica de alta cardinalidad | 17 detectadas |
| OK | Archivo bajo 100 MB | 16.7 MB |
| OK | Sin filas duplicadas exactas | ninguna |

## Resultado

El conjunto **cumple** los requisitos mínimos.