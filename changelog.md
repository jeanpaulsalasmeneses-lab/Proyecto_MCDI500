# Registro de cambios — Proyecto MCDI500 · Grupo 7

**Proyecto:** Exposición operacional documentada de las 15 comunas más pobladas de Chile a las fallas del Sistema Eléctrico Nacional (2024–2026).
**Asignatura:** Programación para la Ciencia de Datos (MCDI500), Magíster en Ciencia de Datos e Inteligencia Artificial, Universidad Andrés Bello.
**Integrantes:** Jairo Barraza Salazar, Javier Huamani Barrera, Jean Salas Meneses y Pavel Chávez San Martín.

Este archivo registra los cambios significativos de F1 a F4: la **fecha**, la **descripción**, el **commit** y la **justificación técnica**. Cada hash se puede verificar con `git show <hash>`. El historial completo está en `git log`, y `git shortlog -sn --no-merges` muestra los aportes por integrante; `.mailmap` unifica las identidades.

Las decisiones metodológicas citadas (D-01 a D-19) están detalladas en [`docs/decisiones.md`](docs/decisiones.md).

---

## 1. Observaciones formativas y acciones de mejora

Cada observación recibida, qué se hizo y dónde quedó. Las observaciones se registraron como issues: las de la Formativa 1 en los #8 a #13, las de la Sumativa 1 en los #30 a #40 y las de la Sumativa 2 en los #55 a #66 (etiqueta `feedback-f3`). Cada PR que resuelve una observación la cierra con «Closes #N».

### Formativa 1 (retroalimentación del 2026-11-07)

| Observación | Acción | Commit (PR) | Impacto |
|---|---|---|---|
| El título y la pregunta no coincidían con el alcance de las 15 comunas más pobladas (#8) | Título y pregunta analítica alineados en F1, F2 y README | `f93cada` (#14) | Problema delimitado; F1 a F4 responden la misma pregunta |
| Faltaba un denominador para comparar comunas (#9) | Frecuencia por 100.000 habitantes-año con la población del Censo 2024 | `929eb18` (#14), D-06 | La normalización cambia la posición de 10 de las 15 comunas |
| No estaba definido cómo tratar los informes sin fecha de término (#10) | Patrón analizado: los faltantes son exactamente los informes pendientes y anulados | `f5030ec` (#14), D-05 | La duración solo usa informes finalizados y no imputa fechas |
| La homologación CEN–INE estaba escrita en el código (#11) | Tablas en `data/reference/` y registro de decisiones | `8187e22` (#14), D-02 y D-03 | Reglas revisables sin ejecutar el notebook; 100 % homologado |
| Faltaba el paso de obtención de los datos originales (#12) | `src/descargar_cen.py` y `docs/descargas_cen.csv` (URL, SHA-256 y fecha) | `9452705` (#14) | Los 33 ZIP se pueden volver a descargar y verificar |
| Tamaño de letra del mapa y acceso al repositorio (#13) | Mapa a 11 pt, verificado con `assert` | `a1cfb26` (#14) | Mapa legible en tamaño carta |
| (Detectado por el grupo) Los CSV cambiaban entre Windows y Linux | `.gitattributes` con `*.csv -text` y `lineterminator="\n"` | `f839b57` (#14), D-04 | Mismo SHA-256 en cualquier equipo |

### Sumativa 1 (92/99, retroalimentación del 2026-11-12)

| Observación | Acción | Commit (PR) | Impacto |
|---|---|---|---|
| La introducción describía F3 como análisis | F3 se describe como núcleo algorítmico (diseño modular, POO y eficiencia) | `2f7ac50` (#42), `e5ca9a3` (#41) | Fases correctas en el mapa, el README y el informe |
| Commits directos a `main`, mensajes vagos y dos identidades por integrante | `.mailmap`; cambios por PR revisado por otro integrante; mensajes con prefijo (`feat`, `fix`, `docs`) | `99d083b` (#41); PR #41 en adelante | Una identidad por integrante; los PR #41, #42, #45 y #47 a #49 quedaron aprobados por un integrante distinto del autor |
| El script de consolidación no tenía funciones | Script organizado en 13 funciones con un solo propósito, más `main()` con parámetros | `1de57ae` (#41) | 15 pruebas propias del script |
| Las dependencias declaraban más de lo que usa el proyecto | `requirements.txt` con solo lo que se importa, con versión fija | `8630a8f` (#41), D-11 | De 107 paquetes congelados con `pip freeze` a 9 dependencias (10 con `pytest` en F4) |
| Referencias con restos de herramientas de redacción e institución incorrecta | Referencias de F3 corregidas | `471aea0` (#41) | APA 7 sin restos de herramientas |
| Los notebooks deben entregarse ejecutados completos y en orden | Salidas restauradas tras un `nbstripout` accidental; cifras del texto alineadas con las salidas | `cc10a4c` (#43), `ccdd295` (#46) | Notebooks ejecutados y coherentes con el informe |

### Sumativa 2 (69/69, retroalimentación del 2026-11-21)

| Punto | Observación | Acción | Commit (PR) | Impacto |
|---|---|---|---|---|
| 1 (#55) | Incertidumbre de tasas, medianas y rankings | Intervalo exacto de Poisson, bootstrap de la mediana y marca de baja precisión bajo 30 intervalos | `35d2a40`, `a21d803` (#49, Javier), D-16 | Solo Antofagasta se distingue del resto; Las Condes, Maipú y Viña del Mar quedan como de baja precisión |
| 2 (#56) | Dimensión temporal e indicadores con y sin el apagón | Mapa de calor comuna × mes y peso del 25-02-2025 en F4; gráficas sin el apagón en F2 | `a21d803` (#49, Javier); `8f4643d`, `aeee7c9` (#48, Jairo), D-17 | El día aporta 220 informes; sin él solo cambian de puesto Viña del Mar y Puerto Montt |
| 3 (#57) | «Balckout» se corregía solo en la leyenda | Tabla versionada `data/reference/equivalencias_causas.csv` y `src/causas.py` | `3706d40` (#51), D-15 | Tres errores de escritura del CEN corregidos en F4, con F2 y F3 intactos |
| 3 (#58) | Antofagasta: ¿pocas instalaciones o un período? Panel con y sin la comuna | Concentración por subestación y empresa, frecuencia anual y panel con y sin la comuna (`src/sensibilidad.py`, Figura 508, tablas 409 a 411) | `e94186c` (#67), D-19 | Es la comuna menos concentrada y la primera en los tres años; sin ella, la frecuencia agregada baja un 22,1 % |
| 4 (#59) | Visualizaciones con IC, promedio, n por comuna, mapa de calor y títulos con el hallazgo | Figuras 505, 506 y 507 | `a21d803`, `1470a84` (#49) | Los títulos dicen el hallazgo; la paleta es apta para daltonismo |
| 5 (#60) | Funciones de F4 en `src/` con pruebas de casos conocidos | `src/incertidumbre.py` y `src/temporal.py`, con 16 pruebas | `35d2a40` (#49) | Conteo cero → límite inferior 0; un intervalo → baja precisión |
| 5 (#61) | Versionar la comparación del script de consolidación | `src/verificar_consolidacion.py` y 6 pruebas | `c8e6209` (#53) | Inventario idéntico byte a byte; consolidados idénticos salvo el fin de línea (D-04) |
| 5 (#62) | La ejecución modificaba archivos versionados | Evidencias de F4 fuera de Git; manifiesto de F2 sin fecha; registros de F3 sin intérprete ni versión de Python | `90ce3e6` (#47), `639b3d3` (#50), D-18 | Un clon limpio solo cambia los notebooks y las salidas que dependen del equipo |
| 5 (#63) | D-10 a D-14 seguían como «Propuesta» | Pasan a «Aceptada» | `bfe91cf` (#52) | Registro de decisiones al día |
| 6 (#64) | Aportes de código propios de Jairo y Javier | PR #48 (Jairo) y PR #49 (Javier, con `src/` y pruebas) | #48, #49 | Los cuatro integrantes tienen commits en F4 |
| 7 (#65) | Informe final con «cómo leer este informe» y tabla de hallazgos | En elaboración | — | — |
| 8 (#66) | Video de 5 a 8 minutos con los cuatro integrantes | En elaboración | — | — |

---

## 2. Registro por fase

### F1 · Definición del problema y entorno reproducible

| Fecha | Commit | Autor | Descripción | Justificación técnica |
|---|---|---|---|---|
| 2026-11-03 | `57823ea` | Jean | Definición inicial del proyecto y estructura del repositorio | Punto de partida del ABP |
| 2026-11-05 | `5f6e8b5`, `5b2be2c` | Pavel | Consolidados en `data/processed/` y `requirements.txt` instalable en Linux y macOS (PR #3) | Un clon limpio no ejecutaba F1 (D-01) |
| 2026-11-05 | `464b020` | Pavel | Mapa conceptual rehecho según la rúbrica de la Formativa 1 (PR #4) | Al mapa le faltaban Git, Jupyter y el entorno, que valían 15 de 25 puntos |
| 2026-11-08 | `f93cada` | Pavel | Título y pregunta alineados con las 15 comunas más pobladas | Issue #8 |
| 2026-11-08 | `1017aa2` | Jean | Mapa y objetivo actualizados | Coherencia del mapa con el objetivo general |
| 2026-11-08 | `89e3171` | Pavel | Verificación del entorno y trazabilidad de la ejecución (`src/trazabilidad.py`) | Evidencia de versiones, commit y semilla en F1 y F2 |
| 2026-11-08 | `9479409` | Pavel | Cinco objetivos específicos | Los objetivos deben responder la pregunta, no describir tareas |
| 2026-11-09 | `fe61bf7` | Javier | Procedencia oficial del dataset CEN e INE en `docs/fuente_dataset.md` | Reemplaza la plantilla anterior (issue #1) |
| 2026-11-15 | `2f7ac50` | Pavel | Mapa conceptual con F3 (núcleo algorítmico) y F4 (comunicar) | Observación de la Sumativa 1 sobre F3 |

### F2 · Obtención, exploración y preprocesamiento

| Fecha | Commit | Autor | Descripción | Justificación técnica |
|---|---|---|---|---|
| 2026-11-05 | `012ab14`, `0508933` | Jean | Desarrollo de F2: carga, exploración y procesamiento de las 15 comunas | Fase de preparación de datos |
| 2026-11-06 | `fccef25`, `1a3eea3`, `5218ed2` | Jairo | Estadística de nulos, conteo de filas y columnas, y filas duplicadas | Diagnóstico de calidad antes de transformar |
| 2026-11-08 | `f839b57` | Pavel | CSV con `lineterminator="\n"` y `.gitattributes` | El hash del manifiesto cambiaba entre Windows y Linux (D-04) |
| 2026-11-08 | `8187e22` | Pavel | Homologación CEN–INE en `data/reference/` y registro de decisiones | Issue #11 (D-02, D-03) |
| 2026-11-08 | `f5030ec` | Pavel | Patrón de informes sin fecha de término (§6.10.5) | Issue #10 (D-05) |
| 2026-11-08 | `929eb18` | Pavel | Denominador poblacional para comparar comunas (§6.13.7) | Issue #9 (D-06) |
| 2026-11-08 | `9452705` | Pavel | Descarga reproducible desde el bucket público del CEN | Issue #12 |
| 2026-11-08 | `4840e24` | Pavel | Diagnóstico de atípicos de la duración, con alternativas medidas | D-08 |
| 2026-11-08 | `0afc893` | Pavel | Roles de las 28 variables, conciliados con la propuesta de Jairo | Issue #7 (D-09) |
| 2026-11-14 | `681f3ca` | Jairo | Cardinalidades de entrada heredadas desde F2 (PR #27) | Trazabilidad entre F2 y F3 |
| 2026-11-15 | `ac20b8e` | Pavel | Spearman calculado sin SciPy | No agregar una dependencia por un solo cálculo |
| 2026-11-22 | `8f4643d` | Jairo | Gráficas 1B, 2B y 3B sin el apagón del 25-02-2025 (PR #48) | Punto 2 de la retroalimentación de F3 (D-17) |
| 2026-11-24 | `aeee7c9` | Pavel | F2 reejecutado con *Restart & Run All*, sin modificar el manifiesto (PR #48) | La numeración debe ser continua desde 1 |

### F3 · Núcleo algorítmico, POO y eficiencia

| Fecha | Commit | Autor | Descripción | Justificación técnica |
|---|---|---|---|---|
| 2026-11-12 | `d706467`, `9b5a142` | Jean | Inicio de F3: núcleo, clases y medición de eficiencia (PR #25 y #26) | Primera versión del núcleo |
| 2026-11-15 | `2ddb632` | Jean | Últimos apartados de F3 (PR #29) | Recursividad, reproducibilidad y conclusiones |
| 2026-11-15 | `471aea0`, `b597432` | Pavel | Referencias corregidas y CSV de F3 idénticos en Windows y Linux | Observaciones de la Sumativa 1 (issues #37 y #38) |
| 2026-11-15 | `8630a8f` | Pavel | `requirements.txt` con 9 dependencias fijas | D-11 (issue #35) |
| 2026-11-15 | `99d083b` | Pavel | `.mailmap`: una identidad por integrante | Observación de control de versiones de la Sumativa 1 |
| 2026-11-15 | `1de57ae` | Pavel | Script de consolidación en 13 funciones, con 15 pruebas | Observación de codificación de la Sumativa 1 (issue #30) |
| 2026-11-15 | `ad0eba6` | Pavel | Núcleo en `src/` como fuente única, importado por el notebook | Evita duplicar la lógica (D-10, issue #31) |
| 2026-11-15 | `b71e6fe` | Pavel | Clases que aprenden de los datos (Template Method), pipeline y equivalencia exacta con F2 | D-12 (issues #32 y #33) |
| 2026-11-15 | `a84a15d` | Pavel | Eficiencia: bucle de F2 frente a la versión vectorizada | 1,83 veces más rápida y 36 % menos memoria (D-13) |
| 2026-11-15 | `e5ca9a3` | Pavel | Decisiones de F3 y recursividad comparativa | D-14 (issue #28, propuesta de Jairo) |
| 2026-11-16 | `cf1bda6`, `540fad1` | Javier | Verificación en Windows 11 y procedimiento de verificación independiente | Reproducibilidad en un segundo equipo |
| 2026-11-17 | `9961cc6` | Pavel | Generadores de informes leen Git como UTF-8 (PR #44) | En Windows, «Chávez» no coincidía y la tabla de autores quedaba en 0 |
| 2026-11-17 | `46a2dde` | Jairo | Revisión del informe de avance de F3 (PR #45) | Detectó cifras de eficiencia desalineadas |
| 2026-11-17 | `ccdd295` | Pavel | Cifras de §5.4 y §9 alineadas con las salidas (PR #46) | Respuesta a la revisión de Jairo |

### F4 · Visualización y comunicación de resultados

| Fecha | Commit | Autor | Descripción | Justificación técnica |
|---|---|---|---|---|
| 2026-11-21 | `8ae8049`, `c2dac8a` | Jean | Notebook `F4_Comunicacion_Resultados.ipynb`: tablas 401 a 403, figuras 501 a 504, validaciones contra F3, interpretación, discusión y conclusiones (PR #47) | Comunicación de los cuatro indicadores sin volver a procesar los datos |
| 2026-11-23 | `35d2a40` | Javier | `src/incertidumbre.py` y `src/temporal.py`, con 16 pruebas (PR #49) | Puntos 1, 2 y 5 de la retroalimentación de F3 (D-16) |
| 2026-11-23 | `a21d803` | Javier | Notebook de incertidumbre y evolución mensual: figuras 505 a 507 y tablas 405 a 408 (PR #49) | Figuras con incertidumbre y títulos que dicen el hallazgo |
| 2026-11-24 | `90ce3e6` | Pavel | Las evidencias de ejecución `F4_90x` dejan de versionarse (PR #47) | Guardaban la fecha y rutas locales (D-18) |
| 2026-11-24 | `c6036eb` | Pavel | El notebook F4 corre completo con *Restart & Run All* (PR #47) | Una celda usaba variables de celdas eliminadas (NameError) |
| 2026-11-24 | `1470a84` | Pavel | Ajustes de revisión: sin advertencias de pandas y coma decimal en la Fig. 506 (PR #49) | Notebook sin advertencias; mismo formato que el informe |
| 2026-11-24 | `639b3d3` | Pavel | Ejecutar los notebooks no modifica archivos versionados (PR #50) | Punto 5 de la retroalimentación de F3 (D-18) |
| 2026-11-24 | `3706d40` | Pavel | Tabla versionada de equivalencias de causas (PR #51) | Punto 3 de la retroalimentación de F3 (D-15) |
| 2026-11-24 | `bfe91cf` | Pavel | README con F4 completo; D-10 a D-14 aceptadas; D-16 a D-18 (PR #52) | Punto 5 de la retroalimentación de F3 |
| 2026-11-24 | `c8e6209` | Pavel | Comparación versionada del script de consolidación (PR #53) | Punto 5 de la retroalimentación de F3 |
| 2026-11-24 | `e94186c` | Pavel | Sensibilidad a Antofagasta: `src/sensibilidad.py`, 11 pruebas, Figura 508 y tablas 409 a 411 (PR #67) | Punto 3 de la retroalimentación de F3 (D-19) |

---

## 3. Síntesis del impacto de las mejoras

| Dimensión | Antes | Ahora | Evidencia |
|---|---|---|---|
| **Modularidad** | Lógica de F2 y F3 dentro de las celdas; script de consolidación sin funciones | 15 módulos en `src/` (una sola versión) que los notebooks importan; script de consolidación en 13 funciones | `ad0eba6`, `1de57ae`, `35d2a40`, `3706d40`, `e94186c` |
| **POO** | Clases que no guardaban estado | Dos jerarquías abstractas (`Transformador` con Template Method y `FuenteDatos`), clases solo donde se aprende de los datos | `b71e6fe`, D-12 |
| **Rendimiento** | Bucle fila a fila de F2 | Versión vectorizada 1,83 veces más rápida y con 36 % menos memoria, con resultado idéntico | `a84a15d`, D-13 |
| **Validación** | Sin pruebas automatizadas | 79 pruebas (casos normales, límite y excepciones), equivalencia exacta con F2 y comparación versionada de la consolidación | `1de57ae`, `b71e6fe`, `35d2a40`, `3706d40`, `c8e6209`, `e94186c` |
| **Reproducibilidad** | 107 paquetes congelados; CSV distintos entre sistemas; ejecución que dejaba archivos modificados | 10 dependencias fijas; CSV idénticos entre sistemas; un clon limpio ejecuta F1 a F4 sin errores y sin dejar cambios espurios | `8630a8f`, `f839b57`, `639b3d3` |
| **Comunicación** | Figuras sin incertidumbre y con títulos que describen el tema; lectura conjunta dominada por una comuna sin advertirlo | Figuras con intervalos de confianza, n por comuna, baja precisión marcada y títulos que dicen el hallazgo; cifras del conjunto con y sin Antofagasta | `a21d803`, `1470a84`, `e94186c` |
| **Documentación y colaboración** | Commits directos a `main` y mensajes vagos | 19 decisiones registradas; cambios por PR, la mayoría aprobados por otro integrante; aportes de los cuatro integrantes en F4 | `docs/decisiones.md`; PR #41 a #67 |
