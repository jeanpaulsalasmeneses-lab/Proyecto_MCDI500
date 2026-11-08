# 1. Introducción y contextualización

## 1.1. Entorno y antecedentes

El Sistema Eléctrico Nacional (SEN) abastece a la mayor parte de la población de Chile. El Coordinador Eléctrico Nacional (CEN) coordina su operación y publica cada mes los **informes de falla** de las instalaciones de generación y transmisión, dentro del conjunto *Desconexiones e intervenciones / informes de falla / limitaciones* (Coordinador Eléctrico Nacional [CEN], s. f.). Cada informe identifica la instalación, la causa declarada, las fechas de perturbación y término, el consumo reportado como afectado y, en el campo `Comuna`, uno o más territorios mencionados.

Este proyecto usa las **33 publicaciones mensuales** de enero de 2024 a septiembre de 2026, que suman **18.019 informes y 28 variables originales**, y la tabla oficial de población comunal del **Censo 2024** (Instituto Nacional de Estadísticas [INE], 2025).

## 1.2. Situación que origina el análisis

Las comparaciones territoriales de calidad de suministro en Chile usan indicadores regulatorios como SAIDI y SAIFI. Estos se calculan con **clientes interrumpidos y tiempos efectivos de interrupción** (Comisión Nacional de Energía [CNE], 2024; Superintendencia de Electricidad y Combustibles [SEC], s. f.). Los informes del CEN describen otra cosa: **fallas de instalaciones del sistema**, sin número de clientes. Hoy no existe una vista comunal y reproducible de esos informes, por cuatro razones:

- la información está repartida en 33 archivos comprimidos;
- la comuna viene como texto libre;
- un mismo informe puede mencionar varias comunas separadas por «|»;
- los nombres no coinciden siempre con los nombres oficiales del INE.

## 1.3. Problema y propósito

El problema es **medir y comparar la exposición operacional documentada** de las 15 comunas más pobladas de Chile a las fallas del SEN. Definimos esa exposición como la frecuencia, la recurrencia y la duración de los informes de falla del CEN que mencionan a cada comuna. **No equivale a interrupciones efectivas de suministro**, porque que un informe mencione una comuna no prueba que sus clientes quedaran sin luz.

Este informe documenta el avance de las **Fases 1 y 2**: la definición del problema, el entorno reproducible y el pipeline de obtención, exploración, limpieza, transformación y validación de los datos. Cada cifra que aparece aquí se puede verificar en los notebooks F1 y F2 y en el repositorio.

## 1.4. Justificación técnica

El problema requiere programación por cinco razones:

- **Volumen y dispersión:** 33 archivos que hay que leer, validar y consolidar con trazabilidad hasta la fila de origen.
- **Normalización textual:** 320 denominaciones comunales distintas que deben homologarse con los 346 códigos oficiales del INE.
- **Relación muchos a muchos:** 16.874 informes con comuna generan 23.284 vínculos informe–comuna.
- **Validación sistemática:** 40 pruebas automatizadas en F2 y verificaciones de integridad en cada etapa.
- **Reproducibilidad:** otro equipo debe poder repetir todo el proceso y obtener los mismos archivos. En hojas de cálculo eso no se puede garantizar.

## 1.5. Conexión con las fases del proyecto

| Fase | Aporte al proyecto | Estado |
|---|---|---|
| F1. Definición y entorno | Problema, pregunta, objetivos, alcance, entorno reproducible y mapa conceptual | Desarrollada (este informe) |
| F2. Exploración y preprocesamiento | Obtención, diagnóstico de calidad, limpieza, homologación CEN–INE, transformación y validación | Desarrollada (este informe) |
| F3. Análisis | Indicadores comunales: tasa de exposición, recurrencia, duración y consumo reportado | Proyectada |
| F4. Visualización y comunicación | Visualizaciones comparativas, hallazgos, conclusiones y recomendaciones | Proyectada |

# 2. Definición de la problemática y objetivos

## 2.1. Problemática delimitada

Se analiza **cómo se distribuyen los informes de falla del SEN** publicados por el CEN entre enero de 2024 y septiembre de 2026 **entre las 15 comunas más pobladas de Chile**, según el Censo 2024. La unidad de registro es el **informe de falla** (`id_falla`), y la unidad de comparación es la **comuna**. La relación entre ambas es el **vínculo informe–comuna**: un informe que menciona tres comunas genera tres vínculos, pero sigue siendo un solo informe.

## 2.2. Pregunta analítica

> ¿Cómo se distribuye la exposición operacional documentada a fallas del Sistema Eléctrico Nacional entre las 15 comunas más pobladas de Chile (Censo 2024), entre enero de 2024 y septiembre de 2026, medida como la frecuencia de informes del CEN en relación con su población, la recurrencia temporal y la duración documental de esos informes, y qué parte de esa exposición corresponde a eventos con afectación de consumo reportada?

## 2.3. Objetivos

**Objetivo general.** Analizar comparativamente la exposición operacional documentada a eventos de falla del SEN en las 15 comunas de mayor población censada de Chile, con los informes publicados entre enero de 2024 y septiembre de 2026. Para ello se usan procedimientos reproducibles de ciencia de datos que caracterizan la frecuencia, la recurrencia, la afectación de consumo reportada y la duración documental válida, con sus límites de interpretación explícitos.

| Objetivo específico | Indicador de logro | Fase |
|---|---|---|
| **OE1.** Integrar las 33 publicaciones del CEN con la tabla oficial del Censo 2024, conservando identificadores y procedencia | 33 de 33 meses consolidados; 346 comunas INE con código único | F1–F2 |
| **OE2.** Depurar los 18.019 registros y vincularlos con códigos comunales oficiales, resolviendo las listas multicomuna | Porcentaje de vínculos homologados con el INE (logrado: 100 %) | F2 |
| **OE3.** Seleccionar las 15 comunas más pobladas y caracterizar la cobertura de sus informes | Lista reproducible de 15 comunas; informes y vínculos asociados (1.834 y 1.915) | F2 |
| **OE4.** Cuantificar por comuna informes únicos, informes con consumo afectado, recurrencia temporal y duración documental válida | Cuatro dimensiones por comuna, con criterios de inclusión explícitos | F3 |
| **OE5.** Visualizar, contrastar y comunicar los resultados y sus límites de medición | Al menos 4 visualizaciones, 5 hallazgos, 3 conclusiones y 2 recomendaciones | F3–F4 |

## 2.4. Alcance

Son **decisiones del equipo**:

- **Se aborda:**
  - las 15 comunas con mayor población censada en 2024, sin importar a qué región pertenezcan;
  - los informes de falla del CEN publicados entre enero de 2024 y septiembre de 2026;
  - indicadores descriptivos de exposición documental.
- **Queda fuera:**
  - indicadores regulatorios (SAIDI, SAIFI, clientes-hora interrumpidos);
  - energía no suministrada y pérdidas económicas;
  - modelos predictivos;
  - las solicitudes de trabajo y las limitaciones, que vienen en los mismos ZIP del CEN pero no son informes de falla;
  - el resto de las 331 comunas, salvo como contexto.

## 2.5. Restricciones

Son **condiciones impuestas** por los datos, el tiempo o las herramientas:

- **Datos:** los informes no incluyen el número de clientes afectados. El 40,04 % no tiene fecha efectiva de término, y el 6,35 % no tiene comuna. Las causas vienen parcialmente en texto libre, y el 60,47 % de los informes prioritarios no tiene una causa determinada.
- **Cobertura temporal:** 2026 tiene solo 9 meses publicados, así que las comparaciones anuales deben normalizarse por tiempo observado.
- **Tiempo:** el proyecto se desarrolla en tres semanas; esta entrega corresponde a la primera.
- **Herramientas:** se usa el ecosistema del curso (Python 3.13, pandas, NumPy, matplotlib, Jupyter, Git y GitHub). No se usan sistemas de información geográfica.

## 2.6. Supuestos

1. Una mención de comuna en un informe del CEN indica **exposición documental** de esa comuna, **no** una interrupción de sus clientes.
2. Los nombres de comuna del CEN se pueden homologar con el INE cuando la correspondencia es unívoca y la región declarada en `Zona Afectada` coincide.
3. La población censada es un **normalizador territorial** válido para comparar comunas de distinto tamaño (D-06). No mide clientes, consumo ni infraestructura.
4. La fecha efectiva de término marca el **cierre administrativo** del informe, no necesariamente la reposición del suministro a cada cliente.
5. El conjunto publicado por el CEN es la fuente oficial disponible. Su completitud no se puede auditar contra otra fuente.

## 2.7. Correspondencia con lo desarrollado en F1 y F2

| Elemento de la formulación | Dónde se desarrolla |
|---|---|
| Problema, pregunta, objetivos, alcance y supuestos | F1 §1–§6 |
| OE1: integración CEN–INE | `src/descargar_cen.py`, `src/consolidar_fallas_2024_2026.py`, F2 §6.5 |
| OE2: depuración y homologación | F2 §4–§6.7 y `data/reference/` |
| OE3: selección y cobertura de las 15 comunas | F2 §6.5.2 y §6.8 |
| OE4 y OE5: indicadores y comunicación | Propuestas en F2 §6.10.5, §6.10.6 y §6.13.7; se calculan en F3 y F4 |

# 3. Aplicación de herramientas científicas

Cada herramienta resuelve un problema concreto del proyecto:

| Herramienta | Propósito en este proyecto | Dónde se usa |
|---|---|---|
| **pandas** | Leer CSV y Excel, normalizar, cruzar tablas (`merge` con `validate`), agrupar y exportar | F1 §8.2; F2 en todas las etapas; `src/` |
| **NumPy** | Base numérica de pandas y valores faltantes (`np.nan`); semilla aleatoria | F2 y `src/trazabilidad.py` |
| **matplotlib** | Mapa conceptual y figuras exploratorias guardadas en `F2/figuras/` | F1 §9 y F2 §6.11–§6.13 |
| **Jupyter** | Notebooks con código, salidas y narrativa, uno por fase | `F1/`, `F2/` |
| **Git y GitHub** | Versionar cada cambio, revisar por pull request y registrar decisiones en issues | Historial del repositorio |
| **venv y requirements.txt** | Aislar el entorno y fijar las versiones exactas | `.venv/`, `requirements.txt` |

Las librerías se usan **dentro de funciones**, no en celdas sueltas. Algunos ejemplos son `normalizar_comuna()`, `auditar_asociacion()`, `comparar_alternativas()` y `perfil_variable()` en F2, y `verificar_dataset()` en F1.

La integración del ecosistema se ve en tres señales:

1. **Verificación del entorno al inicio** de cada notebook (F1 §8.1 y §8.1.1, F2 §0).
2. **Rutas relativas**, porque la raíz del proyecto se ubica automáticamente.
3. **Commit y rama** en que se ejecutó cada notebook, impresos por `src/trazabilidad.py`.

# 4. Reproducibilidad técnica

- **Entorno virtual:** `.venv` creado con `venv`, de la biblioteca estándar de Python (Python Software Foundation, s. f.). Los notebooks fallan a propósito si el kernel no es el del entorno virtual.
- **Dependencias:** `requirements.txt` fija **107 paquetes con versión exacta**. `pywinpty` lleva el marcador `sys_platform == "win32"` y solo se instala en Windows.
- **Verificación componente por componente:** `src/trazabilidad.py` compara cada dependencia declarada con la instalada y detiene el notebook si alguna no coincide. En Linux el resultado es **106 de 106** (107 en Windows).
- **Rutas relativas y semilla:** no hay rutas absolutas en el código. La semilla está fija en 2024, aunque el pipeline no usa procesos aleatorios.
- **Integridad de las salidas.** Siguiendo prácticas de computación científica reproducible (Wilson et al., 2017), F2 exporta siete archivos con su SHA-256 en `data/processed/f2/manifest_f2.json` y comprueba que coincidan (§6.15.5). Se agregó `.gitattributes` (`*.csv -text`) porque Git en Windows cambiaba los saltos de línea de los CSV al hacer commit, y eso rompía los hashes en otro equipo (D-04).

**Comprobación en un segundo equipo.** La verificación está registrada en `docs/verificacion_entorno.md`:

- Se clonó el repositorio en una carpeta limpia de **Linux** (Python 3.13), sin los datos originales, y se ejecutaron F1 y F2 completos sin errores. Los **7 de 7** archivos exportados resultaron idénticos byte a byte.
- Los consolidados también se reconstruyeron **desde la fuente original**: se descargaron de nuevo los 33 ZIP con `src/descargar_cen.py`, se ejecutó la consolidación y el contenido resultó idéntico (18.019 registros, ninguna celda distinta).
- El mismo procedimiento quedó documentado para la verificación en Windows.

# 5. Control de versiones

**Convención de commits.** Prefijo y descripción en español:

| Prefijo | Uso |
|---|---|
| `feat:` | Funcionalidad o análisis nuevo |
| `fix:` | Corrección |
| `docs:` | Documentación |
| `data:` | Cambios en los datos |
| `build:` | Entorno y dependencias |
| `merge:` | Integración de ramas |

Los mensajes explican **qué cambió y por qué**, y citan el issue o el criterio de la rúbrica que resuelven (Chacon y Straub, 2014).

**Ramas y pull requests.** Los cambios de mayor alcance se integraron mediante pull request:

| PR | Contenido |
|---|---|
| #2 | Ajuste del texto del problema |
| #3 | Reproducibilidad: datos, `.gitignore` y dependencias |
| #4–#6 | Mapa conceptual y entrega de la Formativa |
| #14 | Correcciones del feedback de la Formativa |
| Este avance | Brechas de la rúbrica de la Sumativa |

**Issues.** El feedback docente de la Formativa se convirtió en seis issues (#8–#13), uno por punto, que los commits cierran con `Closes #n`.

**Contribuciones por integrante.** Commits identificables en el historial al momento de generar este informe (commit `{{COMMIT}}`):

{{TABLA_COMMITS}}

**Mejora pendiente.** Parte del desarrollo de F2 se subió directamente a la rama principal, sin pull request. Desde la Fase 3, todo cambio entra por PR con revisión de otro integrante.

# 6. Documentación del proceso

## 6.1. Flujo de trabajo completo

| Etapa | Entrada | Proceso | Salida |
|---|---|---|---|
| 0. Obtención | Portal del CEN y Censo 2024 | `src/descargar_cen.py` descarga y verifica los 33 ZIP; el Excel del INE se descarga con su SHA-256 | `data/raw/*.zip`, `docs/descargas_cen.csv`, `data/external/` |
| 1. Consolidación | 33 ZIP | `src/consolidar_fallas_2024_2026.py`: lee solo el informe de fallas y agrega trazabilidad (ZIP, CSV, fila) | `data/processed/cen_fallas_2024_2026_{publicaciones,eventos}.csv` |
| 2. Definición | Consolidado | F1: verificación estructural sin transformar, pruebas iniciales y mapa | Diagnóstico de factibilidad y mapa |
| 3. Exploración y calidad | Consolidado | F2 §1–§4: dimensiones, tipos, nulos, duplicados y roles | Diagnóstico y `docs/diccionario_variables.csv` |
| 4. Limpieza y normalización | Consolidado | F2 §5: claves de comuna, separación de listas, estados y consumo | 23.284 vínculos informe–comuna |
| 5. Homologación | Vínculos e INE | F2 §6.5–§6.7: maestro de 346 comunas y equivalencias de `data/reference/` | 100 % homologado; `data/processed/homologacion/` |
| 6. Transformación | Vínculos homologados | F2 §6.8–§6.10: 15 comunas, variables operacionales y temporales, faltantes y atípicos | Informes y vínculos prioritarios |
| 7. Caracterización | Conjunto prioritario | F2 §6.11–§6.13: visualizaciones, causas y denominador | Perfiles comunales y figuras |
| 8. Validación y exportación | Todo lo anterior | F2 §6.14–§6.15: 40 pruebas y exportación con SHA-256 | 7 CSV y `manifest_f2.json` |

## 6.2. Registro de decisiones técnicas

Cada decisión tiene su entrada en `docs/decisiones.md`, con contexto, evidencia, alternativas descartadas y motivo:

| Decisión | Resumen | Impacto medido |
|---|---|---|
| D-01 | Versionar `data/processed/` y no `data/raw/` | Un clon limpio corre F1 y F2 sin descargar nada |
| D-02 | Equivalencias CEN↔INE en archivos versionados | 156 vínculos homologados por 4 equivalencias; 0 sin homologar |
| D-03 | «Sobreestimar» en lugar de «inflar» | Precisión en la redacción del doble conteo |
| D-04 | CSV sin conversión de saltos de línea | SHA-256 idénticos entre Windows y Linux |
| D-05 | Duración solo con informes finalizados | 954 de 1.834 informes prioritarios tienen duración válida |
| D-06 | Tasa por 100.000 habitantes-año para comparar | 10 de 15 comunas cambian de posición respecto del conteo |
| D-07 | Título y pregunta alineados con el criterio poblacional | Coherencia entre F1, F2, README e informe |
| D-08 | Conservar los atípicos y resumir con la mediana | Eliminarlos movería la mediana un −17,5 % |
| D-09 | Rol y selección de las 28 variables; casting a `category` | −98,4 % de memoria en las categóricas, sin cambiar valores |

## 6.3. Enfoques descartados

| Enfoque | Por qué se descartó |
|---|---|
| Conjunto inicial NYC 311 (reclamos de alumbrado público) | Sin vínculo territorial chileno |
| Contar como informes distintos las menciones a varias comunas | Sobreestima la exposición |
| Homologación aproximada automática (*fuzzy matching*) | Podría unir comunas distintas con nombres parecidos |
| Imputar las fechas de término faltantes | Inventaría cierres que no ocurrieron (D-05) |
| Eliminar los atípicos | Borraría eventos documentados reales (D-08) |
| One-hot encoding | No hay modelos que lo requieran (D-09) |

## 6.4. Fragmentos de código comentados

La clave de comparación de comunas (F2 §5) elimina tildes y diferencias de mayúsculas **sin modificar el dato original**:

```python
def normalizar_comuna(valor):
    texto = limpiar_texto(valor)        # espacios y vacíos -> NA
    if pd.isna(texto):
        return pd.NA
    # Separa cada letra de su tilde y descarta la tilde.
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto if not unicodedata.combining(c)
    )
    return texto.upper()      # "Viña del Mar" -> "VINA DEL MAR"
```

La comparación de alternativas para los atípicos (F2 §6.10.6) trabaja sobre **copias** y mide el efecto de cada tratamiento antes de decidir:

```python
def comparar_alternativas(serie):
    _, _, limite = limites_iqr(serie)      # Q3 + 1,5 * IQR
    p99 = serie.quantile(0.99)
    alternativas = {                       # siempre sobre copias
        "a) conservar todo": serie.copy(),
        "b) eliminar atípicos": serie[serie.le(limite)].copy(),
        "c) acotar al p99": serie.clip(upper=p99),
    }
    return pd.DataFrame(
        {n: resumen_duracion(s) for n, s in alternativas.items()}
    ).T
```

# 7. Repositorio GitHub

Repositorio: **{{REPO}}**

```text
Proyecto_MCDI500/
├── F1/F1_Definición.ipynb       Fase 1: problema, entorno, mapa
├── F2/
│   ├── F2_Exploracion_y_Preprocesamiento.ipynb
│   └── figuras/                 figuras exportadas por F2
├── src/
│   ├── descargar_cen.py         obtención de los 33 ZIP del CEN
│   ├── consolidar_fallas_2024_2026.py   ZIP -> CSV
│   └── trazabilidad.py          entorno, versiones, commit
├── data/
│   ├── raw/        ZIP originales (se descargan, no se suben)
│   ├── external/   Censo 2024 del INE (URL y SHA-256)
│   ├── reference/  equivalencias CEN <-> INE
│   └── processed/  consolidados, salidas de F2, homologación
├── docs/           fuentes, decisiones, diccionario, entregas
├── requirements.txt   107 dependencias con versión exacta
└── README.md          descripción e instrucciones
```

El `README.md` describe el proyecto, la estructura, las dependencias y cómo ejecutar cada notebook en Windows y en Linux o macOS. También explica cómo reconstruir los datos desde la fuente original. Cada carpeta de datos tiene su propio `README.md` con su origen, en línea con los principios FAIR para software de investigación: código y datos localizables, accesibles y reutilizables (Barker et al., 2022). La estructura sigue la separación entre datos originales, externos y procesados que recomienda el material del curso (Salinas, 2026b).

# 8. Codificación funcional

| Componente | Funciones | Ejemplos |
|---|---:|---|
| F1 | 13 | `localizar_proyecto`, `verificar_dataset`, `separar_comunas`, `consumo_reportado` |
| F2 | 30 | `normalizar_comuna`, `crear_clave_region`, `auditar_asociacion`, `patron_fecha_termino`, `comparar_alternativas`, `perfil_variable` |
| `src/` | 9 | `descargar`, `zip_valido`, `verificar_dependencias`, `estado_git`, `informe_entorno` |

- **Un propósito por función:** cada una recibe parámetros y devuelve un resultado. Por ejemplo, `limites_iqr(serie, factor=1.5)` devuelve los límites y `resumen_duracion(serie)` los estadísticos.
- **Estructuras de control en lugar de bloques repetidos:** F2 tiene 45 bucles y 69 condicionales. Recorre los 33 períodos, los dos universos de análisis y las 28 variables, en vez de repetir código por columna (Salinas, 2026c).
- **Copias explícitas:** F2 usa `.copy()` en 31 puntos, para que una transformación no altere el conjunto original (Salinas, 2026a).
- **Flujo verificable:** cada etapa imprime sus conteos antes y después, y los `merge` declaran su cardinalidad (`validate="many_to_one"`).

**Limitación declarada.** Parte de F2 todavía está escrita como celdas procedurales extensas. En F3, las funciones reutilizables de normalización y homologación se trasladarán a `src/` para importarlas en lugar de redefinirlas.

# 9. Preprocesamiento y transformación del dataset

## 9.1. Diagnóstico previo

El consolidado tiene **18.019 registros y 40 variables**: 28 originales y 12 de procedencia y derivadas. No hay identificadores duplicados: cada `id_falla` aparece una sola vez en las 33 publicaciones. Las variables con más faltantes son:

| Variable | Faltantes | % |
|---|---:|---:|
| Elemento(s) | 11.460 | 63,60 |
| Distribuidoras Afectadas | 11.210 | 62,21 |
| SubEstación | 9.148 | 50,77 |
| Fecha Efectiva Fin | 7.214 | 40,04 |
| Causa Definitiva | 2.153 | 11,95 |
| Comuna | 1.145 | 6,35 |
| Zona Afectada | 1.092 | 6,06 |
| Consumo | 287 | 1,59 |

## 9.2. Roles de las variables y transformación según el rol (D-09)

Las 28 variables originales tienen un **rol asignado**: identificador, nominal, territorial, fecha, texto libre o procedencia. Cada una tiene también una decisión justificada, publicada en `docs/diccionario_variables.csv`:

- 10 se analizan;
- 6 se conservan para análisis propuestos en F3;
- 11 se descartan del análisis, aunque quedan en los archivos para mantener la trazabilidad;
- 1 es de procedencia.

La selección **coincide en 25 de 28 columnas** con la propuesta de depuración que hizo Jairo Barraza (documento interno del equipo, issue #7). Las tres diferencias se resolvieron con evidencia:

- `Estado` explica todos los faltantes de la fecha de término;
- `Tipo Causa` distingue la causa presunta de la definitiva;
- `Causa Definitiva` es la base de la recurrencia causal.

**Transformaciones según el rol:**

- **Categóricas:** casting a `category`. Reduce la memoria un **98,4 %** (de 6,93 a 0,11 MB) sin cambiar ningún valor, comprobado con `assert`. No se aplica one-hot, porque no hay modelos, ni orden ordinal, porque ninguna categoría tiene un orden natural.
- **Fechas:** conversión a `datetime` en UTC (pandas development team, s. f.-a).
- **Texto territorial:** normalización a claves comparables.

## 9.3. Valores faltantes: patrón, alternativas y decisión (D-05)

Antes de decidir se midió el patrón de la fecha de término faltante (F2 §6.10.5). **No es aleatorio: lo explica por completo el estado administrativo.**

| Estado | Con fecha de término | Sin fecha de término |
|---|---:|---:|
| Finalizado | 10.802 | 0 |
| Pendiente | 0 | 6.138 |
| Anulado | 3 | 1.076 |

Se compararon cuatro alternativas:

| Alternativa | Evaluación |
|---|---|
| Imputar la mediana | Crearía cierres que no ocurrieron |
| Usar la fecha estimada de retorno | Es una estimación, no un cierre |
| Usar la fecha de publicación | Mide un trámite, no el evento |
| **Calcular la duración solo con informes finalizados** | **Elegida** |

Los pendientes cuentan para la frecuencia, pero no para la duración, y los anulados se excluyen de los indicadores (pandas development team, s. f.-b).

**Impacto declarado.** En 2025, el 51 % de los informes prioritarios sigue pendiente. La causa principal es el apagón del 25 de febrero de 2025: el 83,5 % de sus 218 informes prioritarios está pendiente, frente al 39 % del resto del año. Por eso **la duración subrepresenta ese evento**, y las conclusiones de F3 deben decirlo.

## 9.4. Valores atípicos (D-08)

Con la regla IQR, **69 de 954** intervalos de informes finalizados prioritarios son atípicos (7,2 %), y el máximo llega a 1.073 horas. Las tres alternativas se compararon midiendo su efecto:

| Alternativa | Media | Cambio en la media | Mediana | Cambio en la mediana |
|---|---:|---:|---:|---:|
| Conservar todo | 6,65 h | — | 1,60 h | — |
| Eliminar atípicos | 2,52 h | −62,1 % | 1,32 h | −17,5 % |
| Acotar al p99 | 3,74 h | −43,8 % | 1,60 h | 0,0 % |

**Decisión.** Se conservan todos los intervalos, porque son eventos reales con fechas válidas, y la duración se resume con **mediana y percentiles**. La mediana no cambia al acotar los extremos, así que es pertinente para comparar comunas (OE4). Como toda medida robusta, sacrifica sensibilidad a los eventos largos. Por eso, en F3 cada comuna informará también cuántos de sus intervalos son atípicos.

## 9.5. Normalización y homologación territorial (D-02)

Separar el campo `Comuna` por «|» produjo **23.284 vínculos** de 16.874 informes, sin vínculos duplicados. La homologación con el maestro del INE (346 comunas) tuvo tres pasos:

| Paso | Vínculos homologados | % acumulado |
|---|---:|---:|
| Coincidencia exacta de la clave normalizada | 23.128 | 99,33 |
| Equivalencias con validación regional | 128 | 99,88 |
| Equivalencias con validación multirregional | 28 | **100,00** |

Las cuatro equivalencias (Llay Llay, San Vicente de Tagua Tagua, Treguaco y Paiguano) viven en `data/reference/equivalencias_comunas.csv`. Ninguna corresponde a las 15 comunas analizadas.

## 9.6. Normalización por población (D-06)

Para comparar comunas de distinto tamaño, la exposición se expresa como **informes no anulados por 100.000 habitantes-año**. Los años observados son 33 meses / 12 = 2,75. El conteo absoluto no crece con la población (Spearman = −0,27), y al pasar a la tasa **10 de las 15 comunas cambian de posición**: por ejemplo, Puente Alto baja del 3.º al 8.º lugar. La tasa se informa siempre junto con el conteo, y se declara que el resultado depende del denominador.

## 9.7. Conjunto resultante

| Archivo (`data/processed/f2/`) | Registros | Columnas | Contenido |
|---|---:|---:|---|
| 01_cen_documental_procesado | 18.019 | 51 | Informes con variables normalizadas y temporales |
| 02_cen_asociaciones_auditadas | 23.284 | 12 | Vínculos informe–comuna homologados y auditados |
| 03_cen_informes_prioritarios | 1.834 | 51 | Informes de las 15 comunas |
| 04_cen_fallas_comunas_integrado | 1.915 | 41 | Vínculos prioritarios integrados (entrada de F3) |
| 05_cen_perfiles_15_comunas | 15 | 20 | Perfil por comuna |
| 06_cen_recurrencia_causal_comunal | 181 | 7 | Recurrencia de causas por comuna |
| 07_cen_validaciones_tecnicas | 40 | 5 | Resultado de las 40 pruebas |

**Coherencia con los objetivos.** Cada transformación responde a un objetivo:

- la homologación, a OE2;
- la selección poblacional, a OE3;
- el tratamiento de faltantes y atípicos y el denominador, a OE4;
- la conservación de la procedencia y de las columnas originales, a la trazabilidad que exige todo el proyecto.

# 10. Validación técnica y verificación del código

- **F1:** 6 pruebas de casos normales, límite y excepciones: CSV válido, archivo ausente, archivo vacío, columna territorial ausente, separación de nombres repetidos y clasificación de consumo. Todas aprobadas.
- **F2:** 40 pruebas automatizadas en 10 grupos, todas aprobadas y exportadas a `07_cen_validaciones_tecnicas.csv`:

| Grupo | Pruebas | Grupo | Pruebas |
|---|---:|---|---:|
| Normalización | 5 | Integridad documental | 4 |
| Auditoría geográfica | 4 | Integridad territorial | 4 |
| Clasificación operacional | 5 | Conjunto prioritario | 5 |
| Conversión temporal | 5 | Calidad temporal | 3 |
| Control de excepciones | 1 | Consistencia causal | 4 |

- **Comprobaciones en cada etapa:** F2 contiene 149 instrucciones `assert` que detienen la ejecución donde se origina un problema. Algunas comprueban que no se pierdan informes, que no se dupliquen vínculos, que las tablas cuadren y que el casting no cambie valores. Otras **fijan la evidencia de las decisiones**: si datos nuevos rompen el patrón de la D-05, el notebook avisa que hay que revisarla.
- **Evidencia conservada:** los notebooks se entregan **con sus salidas**: conteos antes y después, tablas y perfiles del conjunto final.

# 11. Notebook F1: definición y entorno

`F1/F1_Definición.ipynb` contiene:

- **Celdas narrativas:** problemática, pregunta, objetivos, alcance, metodología y referencias.
- **Verificación del entorno:** versión de Python, entorno virtual, 106 dependencias, commit y semilla.
- **Verificación estructural del consolidado:** reconocimiento inicial de los datos.
- **Seis pruebas iniciales.**
- **El mapa conceptual.**

**Alcance respetado:** F1 **no limpia, no imputa ni transforma**. Lee el CSV sin modificarlo y solo calcula resúmenes. El notebook corre completo con *Restart Kernel and Run All Cells*, con numeración de ejecución continua.

# 12. Notebook F2: exploración y preprocesamiento

`F2/F2_Exploracion_y_Preprocesamiento.ipynb` sigue el flujo que pide la guía, con una celda narrativa al inicio de cada etapa:

| Etapa | Secciones |
|---|---|
| Entorno | §0 |
| Obtención y carga | §1–§3 |
| Exploración y calidad | §4 |
| Limpieza y normalización | §5 |
| Integración y homologación | §6.5–§6.7 |
| Transformación | §6.8–§6.10 |
| Caracterización | §6.11–§6.13 |
| Validación | §6.14 |
| Exportación | §6.15 |
| Conclusiones | §6.16 |

El notebook corre completo, con numeración continua, y exporta el conjunto procesado a `data/processed/`, que es la entrada directa de F3.

# 13. Vinculación del mapa conceptual con el avance

El mapa conceptual de la Formativa 1 se corrigió con la retroalimentación docente (issues #8–#13):

- se agregó la pregunta analítica;
- se agregó la etapa de obtención de los datos;
- todo el texto quedó en 11 pt o más.

El mapa se genera desde F1 (§9). La tabla relaciona cada tipo de elemento del mapa con su implementación:

| Elemento del mapa | Tipo | Estado | Evidencia |
|---|---|---|---|
| Git y GitHub | Herramienta | Implementado | Historial con commits por integrante, PR #2–#6 y #14, issues #8–#13 |
| Python `src/`, Jupyter, pandas y NumPy | Herramienta | Implementado | `src/` (3 módulos), F1 y F2 |
| Pruebas `assert` | Herramienta | Implementado | 6 pruebas en F1, 40 en F2 y 149 `assert` |
| matplotlib | Herramienta | Parcial | Mapa y figuras exploratorias; visualizaciones finales en F4 |
| ① Pregunta | Proceso | Implementado | F1 §3 |
| ② Obtención | Proceso | Implementado | `src/descargar_cen.py`, `docs/descargas_cen.csv` |
| ③ Depuración | Proceso | Implementado | F2 §4–§5 |
| ④ Homologación | Proceso | Implementado | F2 §6.5–§6.7, `data/reference/` |
| ⑤ Caracterizar | Proceso | Parcial | F2 §6.11–§6.13; indicadores finales en F3 |
| ⑥ Comunicar | Proceso | Parcial | Este informe; comunicación de resultados en F4 |
| Retornos del ciclo | Flujo reproducible | Implementado | La depuración obligó a redefinir la pregunta (NYC 311 → CEN); la revisión de asociaciones pendientes devolvió a la homologación (equivalencias y validación multirregional, F2 §6.6.4–§6.6.5) |
| `requirements.txt`, `.venv` y manifiesto SHA-256 | Flujo reproducible | Implementado | `src/trazabilidad.py`, `docs/verificacion_entorno.md` |
| Registro de decisiones y equivalencias | Decisión técnica | Implementado | `docs/decisiones.md` (D-01 a D-09) |
| Tasa documental por 100.000 habitantes | Decisión técnica | Propuesto | F2 §6.13.7 (D-06); cálculo final en F3 |
| `data/raw`, `external`, `reference` y `processed` | Organización del repositorio | Implementado | Carpetas con su propio README |
| F1/ y F2/ | Estructura del notebook | Implementado | Un notebook por fase, con celdas narrativas por etapa |

**Justificación.** Lo implementado coincide con lo que el mapa proyectaba para F1 y F2: herramientas, obtención, depuración, homologación y un flujo reproducible. La validación de F2 lo comprueba. Lo pendiente (⑤ caracterizar, ⑥ comunicar y la tasa documental) sigue siendo pertinente, porque responde directamente a OE4 y OE5, que el plan asigna a F3 y F4. Los dos retornos del mapa ocurrieron de verdad: el conjunto inicial se reemplazó tras la exploración, y la homologación se ajustó después de revisar las asociaciones pendientes.

![Figura 1 (página siguiente). Mapa conceptual del proyecto, generado por F1 §9. Se reproduce a tamaño real, en carta horizontal, para conservar su texto en 11 pt.](docs/mapa_conceptual_F1_impacto_comunal.png)

# 14. Referencias

Barker, M., Chue Hong, N. P., Katz, D. S., Lamprecht, A.-L., Martinez-Ortiz, C., Psomopoulos, F., Harrow, J., Castro, L. J. G., Gruenpeter, M., Martinez, P. A., & Honeyman, T. (2022). Introducing the FAIR principles for research software. *Scientific Data, 9*, artículo 622. https://doi.org/10.1038/s41597-022-01710-x

Chacon, S., & Straub, B. (2014). *Pro Git* (2.ª ed.). Apress. https://git-scm.com/book/es/v2

Comisión Nacional de Energía. (2024). *Norma técnica de calidad de servicio para sistemas de distribución*. https://www.cne.cl/normativas/electrica/normas-tecnicas/ntcsdx2024/

Coordinador Eléctrico Nacional. (s. f.). *Desconexiones e intervenciones / informes de falla / limitaciones* [Conjunto de datos]. https://www.coordinador.cl/operacion/graficos/desconexiones-e-intervenciones/

Instituto Nacional de Estadísticas. (2025). *Resultados del Censo de Población y Vivienda 2024*. https://censo2024.ine.gob.cl/resultados/

pandas development team. (s. f.-a). *pandas.to_datetime*. *pandas documentation*. https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html

pandas development team. (s. f.-b). *Working with missing data*. *pandas documentation*. https://pandas.pydata.org/docs/user_guide/missing_data.html

Python Software Foundation. (s. f.). *venv — Creation of virtual environments*. *Python 3.13 documentation*. https://docs.python.org/3.13/library/venv.html

Salinas, O. (2026a). *Limpieza y transformación de datos tabulares con Pandas* [Apunte]. Universidad Andrés Bello.

Salinas, O. (2026b). *Estructura profesional de un proyecto Python* [Apunte]. Universidad Andrés Bello.

Salinas, O. (2026c). *Tipos, variables, booleanos, condicionales, ciclos, funciones, módulos y excepciones en Python* [Apunte]. Universidad Andrés Bello.

Superintendencia de Electricidad y Combustibles. (s. f.). *Interrupciones eléctricas – SAIDI*. https://www.sec.cl/informe-sec-saidi/

Wilson, G., Bryan, J., Cranston, K., Kitzes, J., Nederbragt, L., & Teal, T. K. (2017). Good enough practices in scientific computing. *PLOS Computational Biology, 13*(6), e1005510. https://doi.org/10.1371/journal.pcbi.1005510

# Anexo A. Declaración de uso de inteligencia artificial

El equipo usó un asistente de inteligencia artificial generativa (Claude, de Anthropic, mediante Claude Code) como apoyo para:

- revisar código;
- proponer las correcciones del feedback docente;
- redactar documentación y mensajes de commit;
- generar el mapa conceptual;
- estructurar este informe.

Todas las cifras provienen de la ejecución de los notebooks y de los archivos del repositorio. El equipo revisó el contenido, tomó las decisiones metodológicas (registradas en `docs/decisiones.md`) y es responsable de cada afirmación. Cada integrante debe poder explicar el código y las decisiones del proyecto.
