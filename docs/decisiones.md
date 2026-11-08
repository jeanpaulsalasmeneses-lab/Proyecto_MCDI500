# Registro de decisiones — Proyecto MCDI500 · Grupo 7

Cada decisión metodológica o técnica que cambie datos, resultados o la forma de trabajar se anota aquí. Las decisiones no se borran: si una se reemplaza, se marca **Reemplazada por D-XX**.

**Estados:**
- **Propuesta:** se discute en el PR o en el issue.
- **Aceptada:** el grupo la aprobó (PR mergeado con review).
- **Reemplazada:** quedó sin efecto por una decisión posterior.

**Formato de cada entrada:** contexto, decisión, alternativas consideradas, motivo, quién la tomó, y dónde se implementa (commit, PR o issue).

---

## D-01 · Los CSV procesados se versionan en `data/processed/`

- **Fecha:** 2026-11-05 · **Estado:** Aceptada (PR #3) · **Responsable:** Pavel, con aprobación del grupo
- **Contexto:** los CSV consolidados estaban en `docs/` y la carpeta `data/` estaba ignorada, así que un clon limpio no podía ejecutar F1.
- **Decisión:** versionar `data/processed/` y no versionar `data/raw/` (los ZIP del CEN se descargan; ver `data/raw/README.md`).
- **Alternativas:** dejar los CSV en `docs/`; versionar también los ZIP.
- **Motivo:** separar el dato original (inmutable, descargable) del dato procesado (reproducible) y que el repo funcione recién clonado.

## D-02 · Homologación de comunas mediante tablas versionadas

- **Fecha:** 2026-11-06 (Jean, en el código de F2) · 2026-11-08 (se pasa a archivos) · **Estado:** Propuesta (issue #11)
- **Contexto:** 4 nombres del CEN no calzan textualmente con el INE (156 vínculos): Llay Llay, San Vicente de Tagua Tagua, Treguaco y Paiguano.
- **Decisión:** las equivalencias viven en `data/reference/equivalencias_comunas.csv` y `equivalencias_regiones.csv`, y F2 las lee. Una equivalencia solo se aplica si la región del INE coincide con la `Zona Afectada` del CEN. Lo que no calce se exporta como no homologado, sin asignarle comuna.
- **Alternativas:** coincidencia aproximada automática (fuzzy matching), descartada porque podría unir comunas distintas con nombres parecidos; diccionario dentro del código, que era la versión anterior y obligaba a ejecutar el notebook para conocer las reglas.
- **Motivo:** trazabilidad y revisión sin ejecutar código. Resultado: 100 % de los vínculos homologados.

## D-03 · «Sobreestimar» en lugar de «inflar» para el doble conteo

- **Fecha:** 2026-11-06 · **Estado:** Aceptada (PR #6) · **Responsable:** grupo (observación de Jairo)
- **Contexto:** contar como informes distintos las menciones a varias comunas sobreestima la exposición.
- **Decisión:** usar «sobreestimar» y explicar el mecanismo (un informe se contaría más de una vez).
- **Alternativas:** «inflar» (puede leerse como «inflar las cifras»), «aumentar» (pierde la idea de que el aumento es artificial) y «abultar» (coloquial).
- **Motivo:** es el término neutro para un sesgo de medición.

## D-04 · Los CSV se guardan sin conversión de saltos de línea

- **Fecha:** 2026-11-08 · **Estado:** Propuesta (PR de feedback de la Formativa)
- **Contexto:** Git en Windows cambiaba `\r\n` por `\n` dentro de los CSV al hacer commit, y el SHA-256 de `manifest_f2.json` no coincidía en otro equipo.
- **Decisión:** `.gitattributes` con `*.csv -text`, y `lineterminator="\n"` en todos los `to_csv`.
- **Motivo:** que la prueba de ejecución en un segundo equipo dé archivos idénticos byte a byte.
