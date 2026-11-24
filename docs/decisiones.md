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

- **Fecha:** 2026-11-06 (Jean, en el código de F2) · 2026-11-08 (se pasa a archivos) · **Estado:** Aceptada (issue #11; integrada a `main` y evaluada en la Sumativa 1)
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

- **Fecha:** 2026-11-08 · **Estado:** Aceptada (PR de feedback de la Formativa; integrada a `main` y evaluada en la Sumativa 1)
- **Contexto:** Git en Windows cambiaba `\r\n` por `\n` dentro de los CSV al hacer commit, y el SHA-256 de `manifest_f2.json` no coincidía en otro equipo.
- **Decisión:** `.gitattributes` con `*.csv -text`, y `lineterminator="\n"` en todos los `to_csv`.
- **Motivo:** que la prueba de ejecución en un segundo equipo dé archivos idénticos byte a byte.

## D-05 · La duración solo se calcula con informes finalizados; los anulados se excluyen

- **Fecha:** 2026-11-08 · **Estado:** Aceptada (issue #10; integrada a `main` y evaluada en la Sumativa 1) · **Evidencia:** F2 §6.10.5
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

- **Fecha:** 2026-11-08 · **Estado:** Aceptada (issue #9; implementada en F3 como `frecuencia_100k_hab_anio` y validada en la retroalimentación de la Sumativa 1) · **Evidencia:** F2 §6.13.7
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
- **Resolución:** la tasa es el indicador de comparación y el conteo anual se informa como contexto (F3 §7.1, panel integrado).

## D-07 · Título y pregunta analítica alineados con el criterio de selección

- **Fecha:** 2026-11-08 · **Estado:** Aceptada (issue #8; integrada a `main` y evaluada en la Sumativa 1)
- **Contexto:** el título decía «impacto» y «comunas prioritarias». El proyecto no mide impacto, y el único criterio de selección es la población. La entrega solo mostraba la pregunta metodológica del mapa.
- **Decisión:** el título pasa a ser «Exposición operacional documentada de las 15 comunas más pobladas de Chile a las fallas del Sistema Eléctrico Nacional (2024–2026)». «Comunas prioritarias» se mantiene en el texto como término definido: designa **solo** a las 15 comunas más pobladas. Se agrega una pregunta analítica explícita (F1 §3), distinta de la pregunta metodológica del mapa (§9.1).
- **Alternativas:** reemplazar «prioritarias» en todo F2 (cientos de apariciones en código y texto, con mucho riesgo y poco beneficio); definir prioridad con otro criterio (vulnerabilidad, criticidad), que no tiene un indicador externo verificable (F1 §4.2).
- **Motivo:** que el título diga exactamente lo que se mide y cómo se eligieron las comunas.

## D-08 · Los intervalos atípicos se conservan y la duración se resume con la mediana

- **Fecha:** 2026-11-08 · **Estado:** Aceptada (integrada a `main` y evaluada en la Sumativa 1) · **Evidencia:** F2 §6.10.6
- **Contexto:** la duración documental de los informes finalizados es muy asimétrica. La guía de la Sumativa pide diagnosticar los atípicos y comparar alternativas antes de decidir.
- **Evidencia:**
  - Regla IQR (Q3 + 1,5 × IQR): 1.076 de 10.802 intervalos son atípicos en el conjunto completo (10,0 %), y 69 de 954 en las 15 comunas (7,2 %).
  - En las 15 comunas, eliminar los atípicos baja la media un 62,1 % y la mediana un 17,5 %.
  - Acotar al p99 baja la media un 43,8 % y no cambia la mediana (0,0 %).
- **Decisión propuesta:** conservar todos los intervalos; resumir con mediana y percentiles; informar la media solo junto con su versión acotada al p99; en F3, contar los atípicos por comuna.
- **Alternativas descartadas:**
  - Eliminar los atípicos: borra eventos reales documentados y sesga la mediana.
  - Winsorizar los datos exportados: modifica valores originales sin un error de registro que lo justifique.
- **Motivo:** los extremos son informes finalizados con fechas válidas, no errores de captura. La mediana es robusta frente a ellos.

## D-09 · Rol y selección de las 28 variables originales; categóricas como `category`, sin one-hot

- **Fecha:** 2026-11-08 · **Estado:** Aceptada (concilia el issue #7; integrada a `main` y evaluada en la Sumativa 1) · **Evidencia:** F2 §4.5, `docs/diccionario_variables.csv`
- **Contexto:** la propuesta de Jairo («Depuración data 06.11.26») sugería qué columnas conservar. F2 no tenía una selección documentada por rol, y la guía de la Sumativa pide transformar según el rol de cada variable.
- **Decisión propuesta:**
  - Cada una de las 28 columnas originales queda con rol, perfil medido (% de nulos, valores distintos) y decisión: 10 se analizan, 6 se conservan como propuesta para F3, 11 se descartan del análisis y 1 queda como procedencia.
  - La selección **no borra columnas** de los CSV exportados: todo se conserva para la trazabilidad.
  - Las 6 categóricas analizadas pasan a `category`. La memoria baja un 98,4 % (de 6,93 a 0,11 MB) y los valores no cambian.
  - No se aplica one-hot, porque no hay modelos. No se declara ninguna variable ordinal, porque ninguna tiene un orden natural.
- **Conciliación con la propuesta de Jairo:** coincide en 25 de 28 columnas. Las 3 diferencias se resuelven con la evidencia de F2:
  - `Estado`: explica el 100 % de las fechas faltantes y define los anulados (D-05).
  - `Tipo Causa`: distingue la causa presunta de la definitiva (§6.12).
  - `Causa Definitiva`: es la base de la recurrencia causal (§6.12–6.13).
- **Motivo:** decidir columna por columna con evidencia, y conservar las propuestas de análisis de Jairo para F3 (empresa, subestación, tabla 9-3 de la NTSyCS).

---

# Decisiones de la Fase 3 (Sumativa 2)

## D-10 · El código del núcleo vive solo en `src/`, y los notebooks lo importan

- **Fecha:** 2026-11-15 · **Estado:** Aceptada (PR #41, aprobado por Jean; evaluada en la Sumativa 2) · issue #31 · **Evidencia:** F3 §8.2
- **Contexto:** las 16 funciones y clases de F3 existían dos veces: en las celdas del notebook y en una versión condensada distinta en `F3/modulos/`. La guía de la S2 pide un notebook que importe el código, sin copiarlo.
- **Decisión:** una sola versión en `src/` (`indicadores`, `nucleo`, `recorridos`, `medicion`), tomada del notebook porque es la que produjo los resultados documentados. F3 y `ejecutar_f3.py` la importan.
- **Efecto medido:** los 4 CSV de `F3/resultados/` son idénticos byte a byte antes y después. La celda de §3 pasó de 633 a 212 líneas.
- **Alternativa descartada:** conservar `F3/modulos/`. Las dos versiones podían divergir sin que nadie lo notara.

## D-11 · `requirements.txt` declara solo lo que importa el proyecto

- **Fecha:** 2026-11-15 · **Estado:** Aceptada (PR #41, aprobado por Jean; evaluada en la Sumativa 2) · issue #35
- **Contexto:** la retroalimentación de la S1 pide declarar «solo lo que su código importa, con versión fija». El archivo era un volcado de 107 paquetes, y `nbstripout` estaba sin versión y borraba las salidas de los notebooks.
- **Decisión:** 9 dependencias con versión fija, y se quita `nbstripout`.
- **Efecto medido:** con un entorno nuevo construido solo con esas 9, F1, F2 y F3 corren completos. La prueba destapó una dependencia oculta: el Spearman de F2 necesitaba `scipy`. Se calcula ahora como la correlación de los rangos, con el mismo resultado (−0,27).

## D-12 · Clases solo donde el componente aprende de los datos (patrón Template Method)

- **Fecha:** 2026-11-15 · **Estado:** Aceptada (PR #41, aprobado por Jean; evaluada en la Sumativa 2) · issue #32 · **Evidencia:** F3 §8.4, `src/transformadores.py`
- **Contexto:** la guía de la S2 pide clases solo para los componentes que necesitan recordar algo entre una llamada y otra.
- **Decisión:**
  - `HomologadorComunal`, que aprende las 346 comunas del INE y las 4 equivalencias, y `NormalizadorPoblacional`, que aprende la población, heredan de `Transformador`.
  - `Transformador` fija con *Template Method* el algoritmo común: validar, aprender, exigir el ajuste previo y trabajar sobre una copia.
  - Las operaciones sin estado (normalizar nombres, separar vínculos) siguen siendo funciones.
- **Efecto medido:** el pipeline reorganizado reproduce **exactamente** el resultado de F2 (23.284 × 8, idéntico a `02_cen_asociaciones_auditadas.csv`) y la tasa del panel de F3 en las 15 comunas.
- **Alternativas descartadas:**
  - Convertir todo en clases: agrega estado donde no lo hay.
  - *Strategy* u *Observer*: no hay estrategias intercambiables ni eventos que observar en este flujo. Se prefirió un patrón bien justificado a varios mencionados.

## D-13 · La separación de vínculos usa la versión vectorizada

- **Fecha:** 2026-11-15 · **Estado:** Aceptada (PR #41, aprobado por Jean; evaluada en la Sumativa 2) · **Evidencia:** F3 §5.5
- **Decisión:** el pipeline usa `separar_vinculos_vectorizado`, que tiene el mismo resultado que el bucle de F2.
- **Efecto medido:** de 1,8 a 1,9 veces más rápida (≈ 145 frente a ≈ 76-80 ms) y ≈ 36 % menos memoria pico (5,3 frente a 8,3 MB), con los datos reales (18.019 informes). La complejidad es la misma, O(n·k); la mejora viene de calcular la clave solo para los 320 nombres distintos.

## D-14 · Recursividad: comparativa, no estructural

- **Fecha:** 2026-11-15 · **Estado:** Aceptada (PR #41, aprobado por Jean; evaluada en la Sumativa 2) · issue #28, propuesta de Jairo · **Evidencia:** F3 §2.4.4, §4 y §5.4
- **Contexto:** la guía de la S2 indica usar recursión solo si el problema tiene un caso natural (estructuras anidadas o jerarquías de profundidad variable). Los datos del proyecto son tabulares, y la única jerarquía (región → comuna → tipo de instalación) tiene profundidad fija de 3 niveles.
- **Decisión:** la recursión se implementa solo para compararla con la versión iterativa (§4), y el núcleo usa estrategias iterativas y vectorizadas.
- **Efecto medido:** la versión iterativa fue más rápida en 5 de 6 escalas (§5.4), y evita depender del límite de profundidad de Python.

## D-15 · Las descripciones causales con errores de escritura se corrigen con una tabla versionada, en F4

- **Fecha:** 2026-11-24 · **Estado:** Propuesta (PR #51) · **Responsable:** Pavel · **Evidencia:** `data/reference/equivalencias_causas.csv`, `src/causas.py`, `tests/test_causas.py`, F4 §4 y §5.2
- **Contexto:** el CEN publica descripciones con errores de escritura: «Balckout del sistema» (110 vínculos), «Error de personal u opeador» (15) y «Falla debido accidentes» (2). La retroalimentación de F3 (punto 3) pidió normalizarlas con una tabla de equivalencias versionada, como las comunas (D-02), y no solo en la leyenda de la figura.
- **Decisión:** una tabla escrita a mano en `data/reference/equivalencias_causas.csv`, con la descripción del CEN, la corregida y el motivo. `src/causas.py` la carga y la valida (sin claves repetidas, sin cadenas ni celdas vacías), y F4 la aplica a la copia analítica del panel (Tabla 4.2 y Figura 5.2) y a la auditoría contra F3.
- **Alternativas:**
  - Corregir en F2: cambiaría los CSV de F2 y sus SHA-256, y obligaría a reejecutar F3, con lo que cambiarían los tiempos ya citados.
  - Corregir solo la leyenda: es lo que el profesor observó en F3.
  - Agrupar causas parecidas, como «Flash - over en línea» y «Flashover/arco eléctrico»: son categorías distintas del CEN, y unirlas sería una decisión analítica, no una corrección.
- **Motivo:** se corrige donde se comunica, sin perder la trazabilidad a la fuente. F2 y F3 conservan el texto tal como lo publica el CEN, y la tabla documenta cada corrección.
- **Efecto:** en F4 cambia la descripción predominante de 5 comunas (Valparaíso, Viña del Mar, La Serena, Arica y La Florida). Los conteos y porcentajes no cambian, y la auditoría F4 contra F3 sigue conforme.

## D-16 · Cada indicador comunal se informa con su incertidumbre

- **Fecha:** 2026-11-23 · **Estado:** Aceptada (PR #49, aprobado por Pavel) · **Responsable:** Javier · **Evidencia:** `src/incertidumbre.py`, `tests/test_aportes_f4.py`, F4 (incertidumbre) §3 y §4, tablas 407 y 408, figuras 506 y 507
- **Contexto:** la retroalimentación de F3 (punto 1, prioridad alta) advirtió que las tasas y las medianas se calculan sobre pocos registros en varias comunas (9 intervalos en Las Condes, 13 en Maipú), y que comparar posiciones del ranking sin incertidumbre puede inducir a error.
- **Decisión:**
  - **Frecuencia por 100.000 hab.-año:** intervalo exacto de Poisson al 95 % (Garwood) sobre el conteo de informes no anulados.
  - **Mediana de los intervalos documentales:** intervalo bootstrap por percentiles al 95 %, con 2.000 remuestreos y semilla 500.
  - **Baja precisión:** se marcan las comunas con menos de 30 intervalos elegibles (Las Condes, Maipú y Viña del Mar).
  - **Rankings:** si los intervalos de dos comunas se superponen, se informa que no se distinguen.
- **Alternativas:** intervalo normal aproximado, que falla con conteos bajos y da límites negativos con conteo cero; usar SciPy, que no está en las dependencias (el intervalo exacto se obtiene por bisección con la biblioteca estándar).
- **Efecto:** Antofagasta [41,7–49,8] es la única comuna cuya frecuencia se distingue del resto. Las pruebas cubren los casos que pidió el profesor: un conteo cero da un límite inferior cero, y un solo intervalo queda marcado como de baja precisión.

## D-17 · Los indicadores se muestran también sin el apagón nacional del 25-02-2025

- **Fecha:** 2026-11-23 · **Estado:** Aceptada (PR #48 y #49) · **Responsables:** Jairo (F2 §6.11, gráficas 1B a 3B) y Javier (F4, Tabla 406 y Figura 506) · **Evidencia:** `src/temporal.py` (`peso_de_un_dia`), F4 (incertidumbre) §2.1
- **Contexto:** la retroalimentación de F3 (punto 2) pidió mostrar los indicadores con y sin los meses atípicos, para ver cuánto pesa un solo episodio. El apagón del 25-02-2025 aparece en las 15 comunas a la vez.
- **Decisión:** se informa la frecuencia con y sin ese día, por comuna, sin eliminarlo de los datos. Ambos notebooks usan la misma fecha de exclusión.
- **Efecto:** el día aporta 220 informes en las 15 comunas, entre el 6,1 % y el 19,6 % de los informes de cada una. Sin él, solo Viña del Mar y Puerto Montt cambian de puesto en el ranking. Antofagasta baja de 45,6 a 39,4, pero sigue primera.

## D-18 · Ejecutar los notebooks no modifica archivos versionados

- **Fecha:** 2026-11-24 · **Estado:** Propuesta (PR #50; las evidencias de F4, en el PR #47) · **Responsable:** Pavel
- **Contexto:** la retroalimentación de F3 (punto 5) observó que al ejecutar desde un clon quedaban cambios pendientes en archivos cuyo contenido no cambia: la fecha del manifiesto de F2, la ruta del intérprete y la versión exacta de Python en los registros de F3, y las evidencias de F4, que además guardaban rutas locales.
- **Decisión:** los registros versionados guardan solo lo que depende de los datos. Las evidencias de ejecución de F4 (`F4_90x`) se generan pero no se versionan (`.gitignore`).
- **Alternativas:** mover todos los registros a una carpeta ignorada, lo que haría perder la evidencia versionada de F3 que el informe ya cita.
- **Efecto:** tras ejecutar F1 a F4 en un clon limpio, solo cambian los notebooks, las dos figuras de eficiencia de F3 (el tiempo y la memoria varían en cada ejecución) y el PDF del mapa de F1 (depende de las fuentes instaladas en cada equipo).

## D-19 · Las cifras del conjunto de las 15 comunas se informan también sin Antofagasta

- **Fecha:** 2026-11-24 · **Estado:** Propuesta (PR #67, issue #58) · **Responsable:** Pavel · **Evidencia:** `src/sensibilidad.py`, `tests/test_sensibilidad.py`, `F4/F4_Sensibilidad_Antofagasta.ipynb`, Figura 508 y tablas 409 a 411
- **Contexto:** la retroalimentación de F3 (punto 3) pidió revisar si la frecuencia de Antofagasta depende de pocas instalaciones o de un período acotado, y mostrar el panel con y sin esa comuna para que no domine la lectura nacional.
- **Hallazgos:**
  - **No depende de pocas instalaciones:** es la comuna menos concentrada de las 15 (85 subestaciones y 51 empresas; las 5 más frecuentes reúnen el 46,5 % y el 59,0 %).
  - **No depende de un período:** es primera en 2024, 2025 y 2026, y en 21 de los 33 meses.
  - **Sí pesa en el agregado:** tiene el 7,9 % de la población y el 28,2 % de los vínculos, y sin ella la frecuencia agregada baja un 22,1 % (de 12,74 a 9,93).
- **Decisión:** toda cifra del conjunto de las 15 comunas (frecuencia agregada, promedio de las frecuencias, participación causal y mediana del intervalo) se informa también sin Antofagasta (Tabla 411). Las cifras por comuna no cambian, porque cada una se calcula por separado.
- **Alternativas:**
  - Excluir Antofagasta del análisis: ocultaría a la comuna con más informes, y el patrón es persistente, no un episodio.
  - Informar solo el agregado: una sola comuna mueve más de una quinta parte del resultado.
- **Límite:** el CEN registra la subestación y la empresa que informan la falla, no necesariamente el equipo que la originó. Las cifras describen con qué frecuencia algo aparece en los informes; no explican su causa física.
