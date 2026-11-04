# Procedencia y delimitación del dataset — MCDI500

**Fuente:** NYC 311 / NYC Open Data (organismo público municipal).

**Ficha oficial:** https://data.cityofnewyork.us/d/erm2-nwe9

**Condición:** `complaint_type = 'Street Light Condition'`.

**Intervalo:** del 01-01-2025 al 31-10-2026.

**Extracción:** hasta 5000 registros por periodo (2025 y 2026), ordenados por fecha descendente. No es una muestra probabilística: las inferencias se limitan a esta selección de casos.

**Descargado el:** 2026-11-04 00:48 UTC.

**Archivo:** `data\raw\incidencias_alumbrado_2025_2026.csv`.

**Dimensiones:** 10,000 filas × 19 columnas.

**SHA-256:** `8ea54632a9e288a7b30e885bc6a68aacb1759c1f1280f0df9e3411c837d3f86f`.

**Campos omitidos al preparar el extracto por >60% NA:** location_type.

**Tratamiento de datos:** no se crean registros ni se imputan valores; los campos conservados se mantienen como fueron publicados. La limpieza analítica se realizará por separado en Fase 2.

**Privacidad:** no se solicitan nombres, correos, teléfonos ni direcciones postales de quienes contactaron al servicio 311. Antes de compartirlo públicamente, revisar el contenido textual de resolución.

**Condiciones de uso:** verificar y citar los Términos de Uso del portal NYC Open Data y la ficha de origen.

**Advertencia metodológica:** esta base refleja solicitudes de servicio, no fallas confirmadas de activos ni tiempos de reparación reales. El cierre administrativo de una solicitud no siempre equivale a una reparación.

## Consultas reproducibles

- https://data.cityofnewyork.us/resource/erm2-nwe9.csv?%24select=unique_key%2Ccreated_date%2Cclosed_date%2Cresolution_action_updated_date%2Cagency%2Cagency_name%2Ccomplaint_type%2Cdescriptor%2Cstatus%2Cresolution_description%2Cborough%2Ccommunity_board%2Ccity%2Cincident_zip%2Clatitude%2Clongitude%2Copen_data_channel_type%2Ccouncil_district%2Cpolice_precinct%2Clocation_type&%24where=complaint_type+%3D+%27Street+Light+Condition%27+AND+created_date+%3E%3D+%272025-01-01T00%3A00%3A00%27+AND+created_date+%3C+%272026-01-01T00%3A00%3A00%27&%24order=created_date+DESC%2Cunique_key+DESC&%24limit=5000
- https://data.cityofnewyork.us/resource/erm2-nwe9.csv?%24select=unique_key%2Ccreated_date%2Cclosed_date%2Cresolution_action_updated_date%2Cagency%2Cagency_name%2Ccomplaint_type%2Cdescriptor%2Cstatus%2Cresolution_description%2Cborough%2Ccommunity_board%2Ccity%2Cincident_zip%2Clatitude%2Clongitude%2Copen_data_channel_type%2Ccouncil_district%2Cpolice_precinct%2Clocation_type&%24where=complaint_type+%3D+%27Street+Light+Condition%27+AND+created_date+%3E%3D+%272026-01-01T00%3A00%3A00%27+AND+created_date+%3C+%272026-11-01T00%3A00%3A00%27&%24order=created_date+DESC%2Cunique_key+DESC&%24limit=5000
