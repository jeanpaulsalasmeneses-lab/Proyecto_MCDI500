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

## D-05 · La duración solo se calcula con informes finalizados; los anulados se excluyen

- **Fecha:** 2026-11-08 · **Estado:** Propuesta (issue #10) · **Evidencia:** F2 §6.10.5
- **Contexto:** el 40 % de los informes no tiene `Fecha Efectiva Fin`. El profe pidió analizar el patrón antes de decidir.
- **Evidencia:** la ausencia la explica por completo el estado. Finalizados: 10.802 con fecha y 0 sin fecha. Pendientes: 0 con fecha y 6.138 sin fecha. Anulados: 3 con fecha y 1.076 sin fecha. En 2025 hay un 51 % de pendientes, por el apagón del 25-02-2025 (83,5 % de sus 218 informes prioritarios sigue pendiente). La duración es muy asimétrica: mediana de 1,6 h, promedio de 6,7 h y máximo de 1.073 h.
- **Decisión propuesta:**
  1. Duración solo con informes FINALIZADOS e intervalo no negativo, sin imputar fechas.
  2. Resumir con mediana y percentiles, no con el promedio.
  3. Los PENDIENTES cuentan para frecuencia y recurrencia, pero no para la duración, e informar cuántos quedan fuera por comuna.
  4. Los ANULADOS se excluyen de todos los indicadores de exposición, pero se conservan en los datos.
  5. Declarar que la duración subrepresenta el apagón del 25-02-2025.
- **Alternativas:**
  - Imputar la fecha de fin con la mediana: inventa cierres que no ocurrieron.
  - Usar `Fechas Estimada Retorno`: es una estimación, no un cierre.
  - Usar la fecha de publicación como fin: mide un trámite administrativo, no el evento.
- **Motivo:** no hay forma documentada de conocer la duración de un evento sin cerrar. Imputarla crearía datos sin respaldo.

## D-06 · Denominador para comparar la exposición entre comunas

- **Fecha:** 2026-11-08 · **Estado:** Propuesta, **requiere decisión del grupo** (issue #9) · **Evidencia:** F2 §6.13.7
- **Contexto:** el conteo de informes por comuna es absoluto. El profe pidió definir un denominador para comparar.
- **Evidencia:** el conteo no crece con la población (Spearman = −0,27). Con la tasa por 100.000 hab-año, 10 de 15 comunas cambian de posición; Puente Alto baja del 3.º al 8.º lugar y Antofagasta es 1.ª en ambos.
- **Decisión propuesta:**
  - **Indicador de comparación:** informes únicos no anulados / (población 2024 / 100.000) / años observados.
  - **Contexto:** informar siempre también el conteo anual (informes / años observados).
  - **Años observados:** 33 meses / 12 = 2,75.
- **Alternativas:**
  - Solo conteo: no permite comparar comunas de distinto tamaño.
  - Solo tasa: oculta que la exposición se concentra donde hay infraestructura.
  - Instalaciones o clientes por comuna: es el ideal, pero no está en las fuentes actuales.
- **Motivo:** responde el feedback sin ocultar que el ranking depende del denominador. La población es el mismo criterio con que se eligieron las comunas y es un dato oficial; no se interpreta como clientes afectados.
- **Pregunta abierta:** ¿la tasa es el indicador principal y el conteo el contexto, o al revés?
