# II. Diseño de soluciones algorítmicas eficientes

En este proyecto, la Fase 3 corresponde al **núcleo algorítmico**. El pipeline de la Fase 2 se reorganiza en componentes reutilizables, con diseño modular, orientación a objetos y medición de eficiencia, y dentro de ese núcleo se calculan los indicadores comunales. No se usan datos nuevos ni un pipeline distinto: los mismos 18.019 informes de falla del CEN y la misma tabla del Censo 2024 pasan ahora por un código organizado en `src/`, que se puede probar, medir y reutilizar. Así se corrige la observación de la Sumativa 1, que había descrito la Fase 3 como «análisis».

## II.a. Codificación funcional y arquitectura del script

El código del proyecto vive en **una sola versión**, en la carpeta `src/`, y los notebooks y scripts lo importan (decisión D-10). Cada archivo tiene una responsabilidad:

| Archivo | Responsabilidad | Componentes principales | Entrada → salida |
|---|---|---|---|
| `src/consolidar_fallas_2024_2026.py` | Consolidar las 33 publicaciones del CEN | 13 funciones y un bloque principal `main()` | 33 ZIP → publicaciones, eventos e inventario |
| `src/territorio.py` | Operaciones territoriales sin estado | `normalizar_comuna`, `separar_vinculos_vectorizado`, `cargar_maestro_ine` | informes → vínculos informe–comuna |
| `src/transformadores.py` | Pasos que aprenden de los datos | `Transformador`, `HomologadorComunal`, `NormalizadorPoblacional` | vínculos → vínculos con código INE; conteos → tasas |
| `src/pipeline.py` | Encadenar los pasos | `Pipeline`, `ejecutar()`, `tasa_por_comuna()` | datos originales → resultado, en una llamada |
| `src/indicadores.py` | Indicadores comunales | frecuencia, recurrencia, duración y panel integrado | vínculos → panel de 15 comunas |
| `src/nucleo.py` | Núcleo orientado a objetos | `FuenteDatos`, `FuenteCEN`, `FuenteINE`, `NucleoAnalitico` | fuentes validadas → indicadores |
| `src/recorridos.py` y `src/medicion.py` | Recorridos y medición | recursivo, iterativo, `medir_tiempo`, `medir_memoria` | estructura → total y tiempos |

**Flujo de datos.** Los 33 ZIP del CEN se consolidan en `cen_fallas_2024_2026_eventos.csv`. Desde ahí, `ejecutar()` separa cada informe en vínculos informe–comuna, el `HomologadorComunal` les asigna el código oficial del INE y se agrega el estado administrativo. Después, `tasa_por_comuna()` cuenta los informes no anulados y el `NormalizadorPoblacional` los convierte en tasa por 100.000 habitantes-año. Cada paso recibe una tabla y devuelve otra nueva: ninguno modifica su entrada.

**El script de consolidación, reorganizado.** La retroalimentación de la Sumativa 1 señaló que este script, el componente central del pipeline, no tenía una sola función. Ahora tiene 13 funciones de un solo propósito, cada una con parámetros definidos, y errores de datos que se avisan con un mensaje claro. Sobre los 33 ZIP reales produce **exactamente el mismo contenido** que los archivos versionados: 18.019 informes × 40 variables.

```python
def consolidar(entrada, salida, docs, informar=print):
    tablas, inventario, meses = cargar_publicaciones(entrada)
    # une los 33 meses y normaliza el identificador
    publicaciones = consolidar_publicaciones(tablas)
    eventos, repetidos, sin_id = seleccionar_ultima_version(
        publicaciones)
    # fechas en UTC, duración y validaciones
    eventos = derivar_variables_temporales(eventos)
    exportar_csv(eventos, Path(salida) / "cen_..._eventos.csv")
```

## II.b. Preprocesamiento y transformación del dataset

Como indica la guía, el preprocesamiento **no se rehízo**: es el mismo de la Sumativa 1, ahora encapsulado. Cada transformación conserva su justificación y su efecto medido:

| Transformación | Pertinencia | Impacto medido | Objetivo |
|---|---|---|---|
| Normalizar nombres de comuna (sin tildes, mayúsculas) | Los nombres del CEN y del INE se escriben distinto | 320 nombres distintos llevados a clave comparable | OE2 |
| Separar los informes con varias comunas | Un informe puede mencionar varias comunas | 16.874 informes → 23.284 vínculos, sin duplicados | OE2 |
| Homologar con el código oficial del INE | Permite unir con la población | 99,33 % por coincidencia exacta + 156 vínculos por equivalencia = **100 %** | OE2, OE3 |
| Excluir los informes anulados de los indicadores | Son informes dejados sin efecto (D-05) | 130 de 1.834 informes prioritarios | OE4 |
| Duración solo con informes finalizados, resumida con la mediana | La fecha de término falta en el 100 % de los pendientes; hay valores extremos (D-05, D-08) | 954 de 1.834 informes con duración válida | OE4 |
| Tipificar las variables categóricas | Reduce memoria sin cambiar valores (D-09) | −98,4 % de memoria | — |
| Normalizar por población | Comparar comunas de distinto tamaño (D-06) | 10 de 15 comunas cambian de posición frente al conteo | OE4 |

**Validación del conjunto resultante.** El pipeline reorganizado, ejecutado desde los datos originales, produce un resultado **idéntico** al conjunto procesado de la Fase 2 (sección II.c).

## II.c. Validación técnica y verificación del código

| Escenario | Qué se probó | Ejemplos |
|---|---|---|
| Caso normal | El flujo esperado con datos típicos | Consolidar dos meses; homologar por coincidencia exacta y por equivalencia; calcular una tasa conocida (11 informes, 100.000 habitantes y 33 meses dan 4,0) |
| Caso límite | Situaciones extremas pero válidas | La misma falla publicada dos meses (se conserva la última), un informe sin comuna, un conteo cero, una jerarquía vacía, un CSV en codificación latin-1 |
| Excepción | Entradas que deben fallar con un mensaje claro | ZIP dañado, mes duplicado, columna esencial faltante, población cero o negativa, transformar antes de ajustar, clase abstracta instanciada |

**Evidencia:**
- `tests/` contiene **35 pruebas automatizadas** (15 del script de consolidación y 20 de los componentes de F3). Se ejecutan con un solo comando, `python -m unittest discover tests`, y todas pasan.
- El notebook F3 suma **13 pruebas de la arquitectura orientada a objetos** (4 normales, 2 límite y 7 de excepción) y **15 pruebas de validación integral**, exportadas a `F3/resultados/`.

**Equivalencia con la Fase 2** (notebook F3, §8.4). Es la verificación que la guía considera más importante:

| Comprobación | Resultado |
|---|---|
| Vínculos homologados del pipeline frente a `02_cen_asociaciones_auditadas.csv` (F2) | **Idénticos**: 23.284 filas × 8 columnas |
| Tasa del `NormalizadorPoblacional` frente al panel de F3 | **Idéntica** en las 15 comunas |
| Script de consolidación reorganizado frente a los consolidados versionados | **Idénticos** (33 ZIP del CEN) |

**Reproducibilidad.** El repositorio se clonó en una carpeta nueva, se creó un entorno usando solo `requirements.txt` (9 dependencias con versión fija) y se ejecutaron los tres notebooks completos: F1 (1–5), F2 (1–28) y F3 (1–16), sin errores.

## II.d. Eficiencia y optimización

Se compararon **dos pares de implementaciones**, siempre comprobando primero que dan el mismo resultado y midiendo con `timeit` (tiempo) y `tracemalloc` (memoria) (Python Software Foundation, s. f.-b, s. f.-c):

| Operación | Versión A | Versión B | Tiempo | Memoria pico | Complejidad |
|---|---|---|---|---|---|
| Recorrer la jerarquía región → comuna → instalación (§5.2–§5.4) | Recursiva | Iterativa con pila | B un 4,4 % más rápida en la escala mayor (61.280 asociaciones); más rápida en 5 de 6 escalas | A 0,41 KB · B 0,45 KB | Ambas O(n); espacio O(h) frente a O(w) |
| Separar los 18.019 informes en vínculos (§5.5) | Bucle de F2, informe por informe | Vectorizada con pandas | **B de 1,8 a 1,9 veces más rápida** (≈ 145 frente a ≈ 76–80 ms) | **A 8,3 MB · B 5,3 MB** | Ambas O(n·k) |

**Interpretación.**
- **Recorrido de la jerarquía:** las diferencias son pequeñas. La versión iterativa gana en tiempo, gasta levemente más memoria (guarda los nodos pendientes en una pila) y no depende del límite de profundidad de Python. Se eligió la iterativa (D-14).
- **Separación de vínculos:** la versión vectorizada gana en tiempo y en memoria. La complejidad es la misma; la diferencia está en el costo constante, porque la clave de cada comuna se calcula **solo para los 320 nombres distintos** y no para los 23.284 vínculos. El pipeline usa la versión vectorizada (D-13).
- **Protocolo:** el tiempo es el **mínimo de 7 repeticiones**, el menos afectado por otros procesos del equipo, y se midió con el tamaño real de los datos.

## II.e. Diseño estructurado del código

**Cohesión y acoplamiento.** Cada módulo de `src/` agrupa una sola responsabilidad (tabla de II.a). Las dependencias van en un solo sentido: `pipeline` usa `territorio` y `transformadores`, `nucleo` usa `indicadores`, y ningún módulo depende de los notebooks. **La prueba que propone la guía:** cambiar la forma de homologar obliga a modificar un solo archivo (`src/transformadores.py`) o la tabla de equivalencias de `data/reference/`, sin tocar la carga, los indicadores ni los notebooks.

**Recursividad o división funcional.** Los datos del proyecto son tabulares, y la única jerarquía disponible tiene **profundidad fija** de tres niveles. No hay un problema recursivo natural, por lo que el núcleo usa **división funcional** con estrategias iterativas y vectorizadas. La versión recursiva se implementó solo para compararla (D-14), como sugiere la guía del curso (Universidad Andrés Bello, 2026b).

**Escalabilidad.** Un paso nuevo del pipeline se agrega como una clase hija de `Transformador`, sin modificar el `Pipeline`. Más meses de publicaciones solo agregan datos: el costo de normalizar crece con el número de nombres distintos, que crece mucho más lento que el número de informes.

# III. Implementación de código modular y robusto

## III.a. Programación orientada a objetos

El criterio de diseño fue el de la guía: **una clase solo donde el componente necesita recordar algo entre una llamada y otra** (Universidad Andrés Bello, 2026a). Las operaciones que no aprenden nada siguen siendo funciones.

| Clase | Qué aprende o encapsula | Archivo |
|---|---|---|
| `Transformador` (abstracta) | El contrato común: `ajustar()` aprende y `transformar()` aplica | `src/transformadores.py` |
| `HomologadorComunal` | Las 346 comunas del INE y las 4 equivalencias | `src/transformadores.py` |
| `NormalizadorPoblacional` | La población de cada comuna | `src/transformadores.py` |
| `Pipeline` | La lista ordenada de pasos y su bitácora | `src/pipeline.py` |
| `FuenteDatos` (abstracta) → `FuenteCEN`, `FuenteINE` | La validación propia de cada fuente | `src/nucleo.py` |
| `NucleoAnalitico`, `AnalizadorDuracion` | Las fuentes validadas y el cálculo de los indicadores | `src/nucleo.py` |

**Dónde está cada principio:**

| Principio | Dónde | Evidencia en el código |
|---|---|---|
| Encapsulamiento | `Transformador` | Lo aprendido se guarda en `self._parametros`, y la propiedad `parametros` entrega solo una copia. Una prueba verifica que modificar la copia no altera el componente |
| Herencia | `HomologadorComunal` y `NormalizadorPoblacional` | Heredan `ajustar()` y `transformar()`, y solo implementan `_aprender()` y `_aplicar()` |
| Polimorfismo | `Pipeline.transformar` | Llama a todos los pasos de la misma forma, sin preguntar su clase; también a `FuenteCEN.validar()` y `FuenteINE.validar()` |
| Abstracción | `Transformador(ABC)` y `FuenteDatos(ABC)` | Los métodos `@abstractmethod` impiden instanciar las clases base (Python Software Foundation, s. f.-a) |

```python
class Transformador(ABC):
    def ajustar(self, referencia):     # lo común, escrito una vez
        self._exigir_columnas(referencia, self.columnas_ajuste)
        self._parametros = self._aprender(referencia.copy())
        self._ajustado = True
        return self

    def transformar(self, datos):
        if not self._ajustado:
            raise RuntimeError("llame a ajustar() primero")
        # nunca modifica la entrada: trabaja sobre una copia
        return self._aplicar(datos.copy())
```

## III.b. Documentación de arquitectura y funcionalidad

**Patrón de diseño: Template Method** (Gamma et al., 1994). *Problema que resuelve:* todos los pasos que aprenden de los datos deben validar sus columnas, exigir el ajuste previo y trabajar sobre una copia. Sin el patrón, cada clase repetiría esas reglas, y bastaría olvidarlas en una para que un paso modificara los datos originales o se aplicara sin haber aprendido nada. Con el patrón, la clase base fija el algoritmo (validar → aprender; exigir ajuste → copiar → aplicar), y cada clase hija solo define **qué** aprende y **cómo** lo aplica. Las pruebas de excepción comprueban que ninguna subclase puede saltarse esas reglas.

Se evaluaron y se descartaron otros patrones (D-12): no hay estrategias intercambiables en el flujo (*Strategy*) ni eventos que observar (*Observer*). Se prefirió un patrón bien justificado a varios mencionados de pasada.

**Evolución del código desde la Fase 2:**

| Antes (F2 y la primera versión de F3) | Ahora | Efecto medido |
|---|---|---|
| Script de consolidación sin funciones | 13 funciones con `main()` y 15 pruebas | El mismo resultado sobre los 33 ZIP |
| Núcleo de F3 escrito dos veces (en las celdas y en `F3/modulos/`) | Una sola versión en `src/`, importada | Resultados de F3 idénticos byte a byte |
| Homologación escrita en las celdas de F2 | `HomologadorComunal` + `Pipeline` | Idéntico a la salida de F2 (23.284 × 8) |
| Separación de vínculos con un bucle | Versión vectorizada | 1,8 a 1,9 veces más rápida y 36 % menos memoria |
| `requirements.txt` con 107 paquetes | 9 dependencias del proyecto | Apareció una dependencia oculta (`scipy`), resuelta sin agregarla |

**Registro de decisiones.** Cada decisión de la Fase 3 está en `docs/decisiones.md`, con su contexto, su efecto en cifras y las alternativas descartadas: D-10 (fuente única en `src/`), D-11 (dependencias mínimas), D-12 (clases que aprenden y Template Method), D-13 (versión vectorizada) y D-14 (recursividad comparativa). Organizar el código en módulos con responsabilidad única sigue las recomendaciones de disponibilidad y reutilización de software para investigación reproducible (Barker et al., 2022; Jean-Quartier et al., 2025).

# IV. Repositorio GitHub (F3)

**Estructura.** El repositorio separa las carpetas `F1/`, `F2/` y `F3/` (notebook, `ejecutar_f3.py`, figuras y resultados), `src/` (el código), `tests/` (las pruebas), `data/` (datos originales, externos, de referencia y procesados) y `docs/` (fuentes, decisiones y entregas). El `README.md` explica cómo ejecutar los tres notebooks, el núcleo sin notebook y las pruebas, además de la organización y las dependencias.

**Contribuciones por integrante.** Commits identificables en el historial al momento de generar este informe (commit `{{COMMIT}}`, identidades unificadas con `.mailmap`):

{{TABLA_COMMITS}}

**Control de versiones.** El trabajo de la Fase 3 entró por *pull request*:

| PR | Integrante | Contenido |
|---|---|---|
| #25, #26 y #29 | Jean | Desarrollo inicial del núcleo de F3 |
| #27 | Jairo | Cardinalidades de entrada heredadas de F2 |
| #41 | Pavel (revisado y aprobado por Jean) | Reorganización en `src/`, clases, equivalencia, pruebas y dependencias |
| #42 | Pavel | Mapa conceptual con las fases 3 y 4, y este informe |

**Issues y convención.** La retroalimentación de la Sumativa 1 se convirtió en issues (#30 a #40), que los commits cierran con `Closes #n`. Los mensajes usan prefijos (`feat:`, `fix:`, `docs:`, `build:`, `test:`) y explican qué cambió y por qué.

# V. Notebook ejecutable (F3)

`F3/F3_Nucleo_Algoritmico.ipynb` corre completo con *Restart Kernel and Run All Cells*: ejecución del 1 al 16, sin errores y con las salidas conservadas. Su orden sigue la estructura que recomienda la guía:

| Estructura recomendada | Sección del notebook |
|---|---|
| Contexto y objetivo de la Fase 3 | §1 y §2 (incluye la continuidad desde F2, §2.1) |
| Carga del dataset de la Fase 2 | §2.3 y §2.5 |
| Funciones y clases del núcleo | §3 (estructurado), §4 (recursivo) y §6 (orientado a objetos), importados desde `src/` |
| Mediciones de complejidad y comparación | §5.2–§5.4 (recursivo frente a iterativo) y §5.5 (operación real) |
| Integración y patrón aplicado | §7 (panel integrado) y §8.4 (pipeline y Template Method) |
| Verificación: ¿produce el mismo resultado? | §8.4 (equivalencia con F2) y §8.3 (reproducibilidad independiente) |
| Conclusiones y proyección | §9 |

**Integración con la Fase 2.** El notebook parte de los conjuntos exportados por F2 (1.834 informes, 1.915 asociaciones y 15 comunas, §2.1) y demuestra en la §8.4 que el pipeline reorganizado reproduce la salida de F2. La §8.2 verifica que todo lo que usa el notebook proviene de `src/`, sin copias del código en las celdas.

# VI. Bibliografía

Barker, M., Chue Hong, N. P., Katz, D. S., Lamprecht, A.-L., Martinez-Ortiz, C., Psomopoulos, F., Harrow, J., Castro, L. J. G., Gruenpeter, M., Martinez, P. A., & Honeyman, T. (2022). Introducing the FAIR principles for research software. *Scientific Data*, *9*, Artículo 622. https://doi.org/10.1038/s41597-022-01710-x

Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design patterns: Elements of reusable object-oriented software*. Addison-Wesley.

Jean-Quartier, C., Jeanquartier, F., Stryeck, S., Simon, J., Söser, B., & Hasani-Mavriqi, I. (2025). Sharing practices of software artefacts and source code for reproducible research. *International Journal of Data Science and Analytics*, *20*(3), 2539–2550. https://doi.org/10.1007/s41060-024-00617-7

Python Software Foundation. (s. f.-a). *abc — Abstract Base Classes*. Python documentation. https://docs.python.org/3/library/abc.html

Python Software Foundation. (s. f.-b). *timeit — Measure execution time of small code snippets*. Python documentation. https://docs.python.org/3/library/timeit.html

Python Software Foundation. (s. f.-c). *tracemalloc — Trace memory allocations*. Python documentation. https://docs.python.org/3/library/tracemalloc.html

Universidad Andrés Bello. (2026a). *Apunte de la Fase 3: Núcleo algorítmico, eficiencia y programación orientada a objetos* [Apunte, MCDI500]. https://github.com/magistercienciadatos/Material_Didactico_Semana2

Universidad Andrés Bello. (2026b). *Guía de apoyo — Evaluación Sumativa 2 (Fase 3): Núcleo algorítmico, eficiencia e implementación orientada a objetos* [Guía de evaluación, MCDI500]. https://github.com/magistercienciadatos/Material_Didactico_Semana2

# Anexo A. Pruebas automatizadas (`tests/`)

| Archivo | Grupo | Pruebas | Qué verifica |
|---|---|---:|---|
| `test_consolidar.py` | Funciones individuales | 5 | Nombres de archivo, identificador, columnas, trazabilidad sin modificar la entrada |
| `test_consolidar.py` | Consolidación | 10 | 2 normales, 4 límite y 4 excepciones (ZIP dañado, mes duplicado, columna faltante, carpeta vacía) |
| `test_componentes_f3.py` | Transformador base | 4 | Clase abstracta, ajuste previo, encapsulamiento, validación de entradas |
| `test_componentes_f3.py` | HomologadorComunal | 4 | Coincidencia exacta y equivalencia, comuna sin correspondencia, errores del maestro |
| `test_componentes_f3.py` | NormalizadorPoblacional | 5 | Tasa conocida, conteo cero, población inválida, comuna sin población, período inválido |
| `test_componentes_f3.py` | Territorio, Pipeline y funciones de F3 | 7 | Bucle = vectorizado, polimorfismo y bitácora, recursivo = iterativo, errores |
| **Total** | | **35** | Todas aprobadas |

# Anexo B. Mapa conceptual actualizado

El mapa de la Formativa 1 se actualizó para la Fase 3, como sugirió la retroalimentación de la Sumativa 1. La etapa ⑤ del ciclo es ahora el **núcleo algorítmico** (código en `src/`, clases y medición de eficiencia), y la ⑥ es la comunicación de resultados de la Fase 4. El retorno ⑤ → ④ representa la verificación de equivalencia con la homologación de F2. El mapa se genera desde el notebook F1 (§9), con todo su texto en 11 pt o más.

![Figura B.1 (página siguiente). Mapa conceptual del proyecto, actualizado con las fases 3 y 4. Se reproduce a tamaño real, en carta horizontal.](docs/mapa_conceptual_F1_impacto_comunal.png)

# Anexo C. Declaración de uso de inteligencia artificial

El equipo usó un asistente de inteligencia artificial generativa (Claude, de Anthropic, mediante Claude Code) como apoyo para:

- revisar el código y las referencias;
- reorganizar el pipeline en `src/`;
- escribir pruebas y mensajes de commit;
- estructurar este informe.

Todas las cifras provienen de la ejecución de los notebooks, de las pruebas y del historial del repositorio. El equipo revisó el contenido, tomó las decisiones de diseño (registradas en `docs/decisiones.md`) y es responsable de cada afirmación.
