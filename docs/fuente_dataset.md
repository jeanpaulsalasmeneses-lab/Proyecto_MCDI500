# Procedencia de los datos — Proyecto MCDI500 · Grupo 7

El proyecto usa dos fuentes oficiales chilenas. Las dos se pueden descargar de nuevo y verificar con su SHA-256.

| | Fuente 1: fallas del SEN | Fuente 2: población comunal |
|---|---|---|
| **Organismo** | Coordinador Eléctrico Nacional (CEN) | Instituto Nacional de Estadísticas (INE) |
| **Conjunto** | *Desconexiones e intervenciones / informes de falla / limitaciones* (publicaciones mensuales) | Censo de Población y Vivienda 2024: *Población censada por sexo y edad en grupos quinquenales* |
| **Página** | https://www.coordinador.cl/operacion/graficos/desconexiones-e-intervenciones/ | https://censo2024.ine.gob.cl/resultados/ |
| **Período / corte** | Enero 2024 a septiembre 2026 (33 ZIP mensuales) | Censo 2024 (archivo publicado el 2025-12-04) |
| **Se guarda en** | `data/raw/` (no se versiona; se descarga con un script) | `data/external/ine_censo2024_poblacion_comunal.xlsx` (versionado) |
| **Cómo se obtiene** | `python src/descargar_cen.py` | Descarga directa (ver `data/external/README.md`) |
| **Registro de versión** | `docs/descargas_cen.csv` (URL, bytes, SHA-256 y fecha de publicación de cada ZIP) | SHA-256 en `data/external/README.md` |
| **Lo que se usa** | Solo el CSV `AAAA_MM_informe_fallas.csv` de cada ZIP | Hoja «2»: población censada por comuna, con código comunal |

## Flujo desde la fuente hasta los datos procesados

```text
Portal CEN ──src/descargar_cen.py──► data/raw/*.zip (33)
                                         │
                       src/consolidar_fallas_2024_2026.py
                                         ▼
                     data/processed/cen_fallas_2024_2026_{publicaciones,eventos}.csv
                                         │
Portal INE ──descarga──► data/external/ine_censo2024_poblacion_comunal.xlsx
                                         │            data/reference/equivalencias_*.csv
                                         ▼                 │
                       F2 (normalización, homologación CEN–INE, preprocesamiento)
                                         ▼
                     data/processed/f2/*.csv + manifest_f2.json (SHA-256)
                     data/processed/homologacion/*.csv
```

## Verificación de reproducibilidad (2026-11-08)

Se descargaron de nuevo los 33 ZIP desde el portal del CEN, en Linux, y se ejecutó `src/consolidar_fallas_2024_2026.py`. Los dos consolidados reconstruidos son **idénticos en contenido** a los versionados: 18.019 registros, las mismas 34 y 40 columnas y **ninguna celda distinta**. La única diferencia está en los finales de línea (ver la decisión D-04 en `docs/decisiones.md`). El Excel del INE descargado de nuevo tiene el mismo SHA-256 que el del repo.

## Delimitación y advertencias

- **Unidad de registro:** un informe de falla (`Número` → `id_falla`). Los 18.019 informes **no son** 18.019 cortes de suministro ni eventos independientes con clientes afectados.
- **Comuna:** el campo `Comuna` puede traer varias comunas separadas por `|`. Un informe con varias comunas genera varios **vínculos informe–comuna**, pero no nuevos informes.
- **Población:** se usa para seleccionar las 15 comunas más pobladas y como denominador de comparación (D-06). **No representa clientes afectados.**
- **Indicadores regulatorios:** sin datos de clientes e interrupciones efectivas no se calculan SAIDI ni SAIFI (CNE, 2024).
- **Tratamiento:** no se crean registros ni se imputan valores. Los datos originales se conservan y las columnas derivadas se agregan aparte.

## Historial

Hasta el 2026-11-05 este documento describía un conjunto inicial de NYC 311 (reclamos de alumbrado público de Nueva York). Ese conjunto se descartó y se reemplazó por fuentes oficiales chilenas con información territorial (F1 §10.2; issue #1).

## Referencias

Coordinador Eléctrico Nacional. (s. f.). *Desconexiones e intervenciones / informes de falla / limitaciones* [Conjunto de datos]. https://www.coordinador.cl/operacion/graficos/desconexiones-e-intervenciones/

Instituto Nacional de Estadísticas. (2025). *Censo de Población y Vivienda 2024: Población censada por sexo y edad en grupos quinquenales* [Conjunto de datos]. https://censo2024.ine.gob.cl/resultados/
