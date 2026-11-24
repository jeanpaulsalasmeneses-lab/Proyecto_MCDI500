# 2. Introducción y contextualización

El Coordinador Eléctrico Nacional (CEN) publica cada mes los **informes de falla** del Sistema Eléctrico Nacional (SEN), con la instalación, la causa, las fechas, el consumo reportado y las comunas mencionadas (Coordinador Eléctrico Nacional [CEN], s. f.). El proyecto reúne las **33 publicaciones** de enero de 2024 a septiembre de 2026 (**18.019 informes**) y las cruza con el **Censo 2024** (Instituto Nacional de Estadísticas [INE], 2025).

**Situación y relevancia.** SAIDI y SAIFI miden clientes interrumpidos (Comisión Nacional de Energía [CNE], 2024); los informes del CEN describen fallas de instalaciones, repartidas en 33 archivos y con la comuna como texto libre, y no existe una vista comunal de ellos. Esa vista permite a un municipio, a la Superintendencia o a un equipo de planificación de resiliencia decidir **dónde mirar primero**: qué comunas aparecen más en los informes, si el patrón persiste o se debe a un evento, y con qué precisión puede afirmarse.

**Fases.** F1 definió el problema; F2 obtuvo y depuró los datos; F3 construyó el núcleo algorítmico; F4 agrega incertidumbre, tiempo y sensibilidad, y comunica.

**Cómo leer este informe.** La tabla del apartado 24 indica el notebook y la sección que producen cada cifra; el detalle está en el repositorio (enlace en la portada).

# 3. Definición de la problemática y objetivos

**Problema.** Medir y comparar la **exposición operacional documentada** de las 15 comunas más pobladas de Chile a las fallas del SEN.

> ¿Cómo se distribuye la exposición operacional documentada a fallas del SEN entre las 15 comunas más pobladas de Chile entre enero de 2024 y septiembre de 2026, medida como frecuencia por población, recurrencia y duración de los informes, y qué parte corresponde a eventos con consumo afectado?

**Objetivo general.** Analizar comparativamente esa exposición con procedimientos reproducibles y límites explícitos. **Específicos:** OE1, integrar las 33 publicaciones con el Censo 2024 (F1–F2); OE2, depurar y homologar con los códigos del INE (F2); OE3, seleccionar las 15 comunas y caracterizar su cobertura (F2); OE4, cuantificar frecuencia, recurrencia, consumo afectado y duración (F3); OE5, comunicar los resultados con su incertidumbre (F4).

**Alcance.** 15 comunas; informes del CEN de enero de 2024 a septiembre de 2026; frecuencia, recurrencia causal, duración documental y consumo reportado. No incluye SAIDI, SAIFI ni clientes sin suministro.

**Restricciones.** El CEN no informa clientes afectados; la fecha de término falta en los informes pendientes y anulados; 2026 aporta solo nueve meses.

**Supuestos.** Un informe que menciona una comuna la expone; la población 2024 es un denominador de contexto; los intervalos de Poisson suponen informes independientes.

# 4. Aplicación de herramientas científicas

**pandas** lee los 33 ZIP, separa informes en vínculos y agrupa (McKinney, 2022); **NumPy** hace el bootstrap con semilla fija y las operaciones vectorizadas; **Matplotlib** construye las figuras con paleta apta para daltonismo; **Jupyter** integra código, salida e interpretación en seis notebooks; **Git y GitHub** dan ramas, *pull requests* e issues; **unittest y pytest** ejecutan 79 pruebas. El intervalo de Poisson se calcula por bisección con la biblioteca estándar, sin agregar SciPy por una sola función (D-11), y no se usa seaborn.

# 5. Reproducibilidad técnica

Entorno virtual (`venv`) y `requirements.txt` con **10 dependencias de versión fija**; cada notebook comprueba `sys.prefix != sys.base_prefix`. **Evidencia:** el 24 de noviembre, un clon nuevo de `main` con un entorno creado solo desde `requirements.txt` ejecutó sin errores los seis notebooks, `F3/ejecutar_f3.py` (SHA-256 del panel) y las 79 pruebas, y tablas, figuras y datos quedaron idénticos a los versionados (D-18). Los CSV tienen la misma huella en Windows y Linux (D-04).

# 6. Control de versiones

Desde la Sumativa 1, cada cambio entra por una rama y un *pull request* revisado por otro integrante; las observaciones son issues que el PR cierra con «Closes #N»; los mensajes llevan prefijo (`feat:`, `fix:`, `docs:`) y `.mailmap` unifica las identidades. Commits en `main` (commit `{{COMMIT}}`):

{{TABLA_COMMITS}}

# 7. Documentación del proceso

`docs/decisiones.md` registra **19 decisiones** con contexto, efecto medido y alternativas descartadas. Por ejemplo, **D-15**: «Balckout» y otros dos errores del CEN se corrigen con una tabla versionada aplicada solo en F4, sin alterar F2 ni F3; **D-19**: Antofagasta aporta el 28,2 % de los vínculos con el 7,9 % de la población, así que las cifras del conjunto se dan con y sin ella. `changelog.md` registra cada cambio con fecha, commit, autor y justificación.

# 8. Repositorio GitHub actualizado

Carpetas `F1/` a `F4/`, `src/` (15 módulos), `tests/`, `data/` y `docs/`; el `README.md` da el orden de ejecución. En F4 aportaron código los cuatro: Jean, el notebook de comunicación (PR #47); Javier, incertidumbre y evolución temporal (#49); Jairo, la sensibilidad al apagón en F2 (#48); Pavel, reproducibilidad, causas y sensibilidad a Antofagasta (#50 a #54 y #67).

# 9. Diseño de soluciones algorítmicas eficientes

Los apartados 10 a 15 describen el núcleo de `src/`, con lo agregado en F4.

## 10. Codificación funcional

Un módulo por responsabilidad: `territorio` separa y homologa, `indicadores` calcula el panel, `incertidumbre` los intervalos, `temporal` la serie mensual, `causas` corrige descripciones y `sensibilidad` compara con y sin una comuna. Las funciones reciben parámetros explícitos, no modifican su entrada y fallan con mensaje:

```python
def intervalo_poisson_exacto(conteo, nivel=0.95):
    if not isinstance(conteo, (int, np.integer)) or conteo < 0:
        raise ValueError("El conteo debe ser un entero no negativo.")
    ...
    if conteo == 0:
        return 0.0, superior      # con cero, el inferior es 0
```

## 11. Preprocesamiento y transformación del dataset

| Paso | Justificación | Efecto medido |
|---|---|---|
| Separar informes con varias comunas | No contar dos veces un informe | 16.874 informes → 23.284 vínculos |
| Homologar con el código del INE | Unir con la población | 99,33 % exacto + 156 por equivalencia = 100 % |
| Fechas a `datetime` y duración solo de finalizados | La fecha de término falta en pendientes y anulados (D-05) | 954 intervalos válidos |
| Excluir anulados; conservar atípicos con la mediana | Anulados sin efecto; atípicos reales (D-08) | 130 de 1.834 excluidos |
| Normalizar por población (D-06) | Comparar comunas de distinto tamaño | 10 de 15 cambian de posición |

## 12. Validación técnica y verificación del código

**79 pruebas en 6 archivos**, todas aprobadas: casos normales (11 informes, 100.000 habitantes y 33 meses dan 4,0), límite (conteo cero → límite inferior 0) y excepciones (ZIP dañado, población cero, transformar antes de ajustar). El pipeline de F3 reproduce la salida de F2 **idéntica** (`assert_frame_equal`, 23.284 × 8) y `verificar_consolidacion.py` reconstruye el inventario desde los 33 ZIP con el mismo SHA-256.

## 13. Eficiencia y optimización

Con `timeit` (mínimo de 7 repeticiones) y `tracemalloc`, tras comprobar que dan el mismo resultado (Python Software Foundation, s. f.-a, s. f.-b):

| Operación | Comparación | Tiempo | Memoria pico |
|---|---|---|---|
| Separar 18.019 informes | Bucle frente a vectorizada | Vectorizada **1,8 a 1,9 veces más rápida** (≈ 145 frente a 76–80 ms) | 8,3 → 5,3 MB |
| Recorrer región → comuna → instalación (6 escalas) | Recursiva frente a iterativa | Iterativa 4,4 % más rápida con 61.280 asociaciones | 0,41 frente a 0,45 KB |

Ambas son O(n): la vectorizada gana en costo constante, porque normaliza 320 nombres y no 23.284 vínculos. Se eligieron la vectorizada (D-13) y la iterativa (D-14).

## 14. Diseño estructurado del código

Las dependencias van en un solo sentido y ningún módulo usa los notebooks. La prueba de acoplamiento de la guía: **corregir una causa mal escrita toca 1 archivo**, `equivalencias_causas.csv`, sin cambiar código (D-15).

## 15. Notebook final ejecutado y documentado

Los seis notebooks corren con *Restart & Run All*, numeración continua desde 1 y salidas visibles; F4 tiene tres: comunicación, incertidumbre y sensibilidad.

# 16. Implementación de código modular y robusto

Los apartados 17 y 18 describen las clases y la arquitectura.

## 17. Programación orientada a objetos

Clases solo donde el componente aprende de los datos (D-12; Universidad Andrés Bello, 2026a): `Transformador` es abstracta, y `HomologadorComunal` y `NormalizadorPoblacional` aprenden las comunas y la población.

```python
class Transformador(ABC):
    def ajustar(self, referencia):    # HERENCIA: común
        self._parametros = self._aprender(referencia.copy())
        self._ajustado = True         # ENCAPSULAMIENTO
        return self

for nombre, paso in self.pasos:       # POLIMORFISMO (Pipeline)
    datos = paso.transformar(datos)
```

**Encapsulamiento:** lo aprendido vive en `self._parametros` y la propiedad pública entrega una copia. **Herencia:** las hijas solo implementan `_aprender()` y `_aplicar()`. **Polimorfismo:** `Pipeline.transformar` llama igual a cada paso sin preguntar su clase.

## 18. Documentación de arquitectura

| Componente | Responsabilidad | Archivo en `src/` |
|---|---|---|
| Consolidación | 33 ZIP → informes con procedencia | `consolidar_fallas_2024_2026.py` |
| Transformadores y pipeline | Aprender y aplicar homologación y tasa | `transformadores.py`, `pipeline.py` |
| Indicadores | Panel de las 15 comunas | `indicadores.py`, `nucleo.py` |
| F4 | Intervalos, serie mensual, causas y sensibilidad | `incertidumbre.py`, `temporal.py`, `causas.py`, `sensibilidad.py` |

**Template Method** (Gamma et al., 1994). *Problema:* cada paso debía validar, exigir el ajuste y copiar. *Solución:* la base fija ese algoritmo y las hijas definen qué aprenden. *Sin él,* olvidar una regla en una clase modificaría los datos originales. Una sola versión del código, como recomiendan Wilson et al. (2017).

# 19. Construcción de visualizaciones efectivas

Los apartados 20 y 21 describen cómo se prepararon los datos para graficar y las tres figuras principales.

## 20. Preprocesamiento y transformación de datos

El panel analítico no se grafica directamente: se construyen copias legibles con una matriz comuna × mes con **ceros explícitos** (tabla 405), comunas **ordenadas por frecuencia**, causas corregidas **solo para mostrar** (D-15), coma decimal, unidades en los ejes e intervalos guardados junto al valor (tablas 407 y 408). Así se separa el conjunto que se analiza del que se muestra (Universidad Andrés Bello, 2026b).

## 21. Visualizaciones analíticas

Tres tipos de gráfico distintos, cada título con el hallazgo. Fuente: CEN (2024–2026) e INE (Censo 2024).

![Figura 1. Frecuencia por 100.000 habitantes-año con intervalo exacto de Poisson al 95 % (archivo F4_Figura_506). Muestra: Antofagasta (45,6; IC 41,7 a 49,8) es la única comuna separada de todas. Se infiere: entre vecinas del ranking el orden no es concluyente. Límite: Poisson supone informes independientes.](F4/figuras/F4_Figura_506_Frecuencia_Intervalo_Confianza.png)

![Figura 2. Vínculos informe-comuna por mes (archivo F4_Figura_505; en el notebook, Figura 5.1). Muestra: febrero de 2025 destaca en las 15 comunas a la vez. Se infiere: el apagón eleva a todas, pero no explica el ranking. Límite: se excluye solo el 25-02-2025, no los días cercanos.](F4/figuras/F4_Figura_505_Evolucion_Mensual_Comunal.png)

![Figura 3. Concentración por subestación y frecuencia anual (archivo F4_Figura_508). Muestra: Antofagasta es la comuna menos concentrada y la primera en 2024, 2025 y 2026. Se infiere: su liderazgo es amplio y persistente. Límite: subestación y empresa tal como las informa el CEN.](F4/figuras/F4_Figura_508_Sensibilidad_Antofagasta.png)

# 22. Metodología del desarrollo técnico

**Obtención** (F1–F2) → **depuración** (F2) → **núcleo modular** (F3) → **incertidumbre, tiempo y sensibilidad** (F4). Cada decisión, con su razón y su resultado:

- Normalizar por población, por los tamaños distintos: **10 de 15 cambian de posición** (D-06).
- **Intervalo exacto de Poisson** (Garwood, 1936), porque son conteos pequeños: **solo Antofagasta se distingue** (D-16).
- **Bootstrap de la mediana** (Efron & Tibshirani, 1993), porque la duración es asimétrica: la mediana más alta no se distingue.
- Recalcular **sin el 25-02-2025**, que aporta 220 informes: el ranking **casi no cambia** (D-17).
- **Concentración por subestación** y panel **sin Antofagasta**, porque dominaba el conjunto: patrón amplio y persistente (D-19).

# 23. Validación y reflexión técnica

| Fase anterior | Ahora (F4) | Por qué cambió |
|---|---|---|
| Tasas y medianas sin incertidumbre | Intervalos y baja precisión bajo 30 intervalos | Sin ellos, el ranking parecía exacto (D-16) |
| Solo el período agregado | Serie mensual y cifras sin el apagón | Un día podía explicar el ranking (D-17) |
| 35 pruebas (F3) | 79 pruebas | Cada función de F4 con casos conocidos |

**Reflexión.** Recursivo e iterativo difieren poco (4,4 %); vectorizar casi reduce el tiempo a la mitad, y ahí se puso el esfuerzo. La escalabilidad depende de los nombres de comuna, que crecen más lento que los informes.

# 24. Resultados

| N.º | Hallazgo | Cifra | Notebook · § |
|---|---|---|---|
| H1 | Antofagasta, la mayor frecuencia; Maipú, la menor | 45,60 frente a 2,53 por 100.000 hab.-año | Comunicación · 4.7 |
| H2 | Tres causas, la más frecuente en 5 comunas cada una | Terceros, baja frecuencia y *blackout* | Comunicación · 4.7 |
| H3 | El consumo reportado varía 52 puntos | Viña del Mar 83,8 %; La Florida 31,8 % | Comunicación · 5.4.6 |
| H4–H6 | Febrero de 2025 destaca, pero no explica el ranking | 283 vínculos (6,6 × la mediana); sin el día, solo cambian los puestos 11 y 12 | Incertidumbre · 2 |
| H7–H8 | Solo Antofagasta se distingue | IC 41,7 a 49,8; 13 de 14 pares vecinos se superponen | Incertidumbre · 3 |
| H9–H10 | La duración no ordena a las comunas | Valparaíso 3,47 h (IC 1,96 a 5,87); 3 con baja precisión | Incertidumbre · 4 |
| H11–H14 | Antofagasta: amplia, persistente y con peso | 85 subestaciones; 1.ª los tres años; sin ella, 12,74 → 9,93 | Sensibilidad · 2–5 |

Para OE4 y OE5: la exposición se concentra en una comuna, persiste y no la explica un evento.

# 25. Discusión

La hipótesis de F1, que más población implicaría más exposición, no se cumple: el conteo no crece con la población (Spearman = −0,27); encabezan Antofagasta, Arica y Rancagua, y cierran Las Condes y Maipú. **Limitaciones:** se cuentan informes, no cortes a clientes; Poisson supone independencia y el apagón la viola; la duración solo usa informes finalizados, y los pendientes podrían ser los más largos; 2026 tiene nueve meses. Los resultados son asociaciones documentales, no causas.

# 26. Conclusiones

1. Solo Antofagasta se distingue (45,6; IC 41,7 a 49,8); el resto del ranking se lee por grupos, no por puestos.
2. El apagón eleva a todas las comunas, pero sin él el ranking casi no cambia: los patrones son comunales.
3. El liderazgo de Antofagasta es amplio (85 subestaciones) y persistente (1.ª los tres años), y desplaza un 22,1 % la lectura conjunta.

**Mejoras.** Cruzar con los clientes afectados de la SEC para pasar de informes a cortes, y revisar las fallas de terceros en Antofagasta, la causa más frecuente.

# 27. Trazabilidad de mejoras

Observaciones de la Sumativa 2; la tabla completa desde la Formativa 1 está en `changelog.md`.

| Observación (S2) | Acción | Commit (PR) | Impacto |
|---|---|---|---|
| Incertidumbre (#55) y tiempo (#56) | `incertidumbre.py`, `temporal.py`, 16 pruebas | `35d2a40`, `a21d803` (#49) | Solo Antofagasta se distingue |
| «Balckout» solo en la leyenda (#57) | Tabla de equivalencias y `causas.py` | `3706d40` (#51) | 3 errores corregidos en un archivo |
| Antofagasta (#58) | `sensibilidad.py`, Figura 508 | `e94186c` (#67) | Patrón amplio y persistente |
| Consolidación sin comparar (#61) | `verificar_consolidacion.py` | `c8e6209` (#53) | Inventario idéntico byte a byte |
| La ejecución modificaba archivos (#62) | Salidas del equipo fuera de Git | `639b3d3` (#50) | Clon limpio sin cambios espurios |

# 28. Presentación audiovisual

Canvas Studio, 5 a 8 min: [enlace pendiente]. Apertura (Jean), datos (Jairo), metodología (Pavel), demostración (Jean), Figuras 1–2 (Javier), Figura 3 (Pavel), límites (Jairo), cierre (Jean).

# 29. Bibliografía

Comisión Nacional de Energía. (2024). *Norma técnica de calidad de servicio para sistemas de distribución*. https://www.cne.cl/normativas/electrica/normas-tecnicas/ntcsdx2024/

Coordinador Eléctrico Nacional. (s. f.). *Desconexiones e intervenciones / informes de falla / limitaciones* [Conjunto de datos]. https://www.coordinador.cl/operacion/graficos/desconexiones-e-intervenciones/

Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall.

Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design patterns: Elements of reusable object-oriented software*. Addison-Wesley.

Garwood, F. (1936). Fiducial limits for the Poisson distribution. *Biometrika*, *28*(3/4), 437–442. https://doi.org/10.1093/biomet/28.3-4.437

Instituto Nacional de Estadísticas. (2025). *Resultados del Censo de Población y Vivienda 2024*. https://censo2024.ine.gob.cl/resultados/

McKinney, W. (2022). *Python for data analysis: Data wrangling with pandas, NumPy, and Jupyter* (3.ª ed.). O'Reilly Media.

Python Software Foundation. (s. f.-a). *timeit — Measure execution time of small code snippets*. Python documentation. https://docs.python.org/3/library/timeit.html

Python Software Foundation. (s. f.-b). *tracemalloc — Trace memory allocations*. Python documentation. https://docs.python.org/3/library/tracemalloc.html

Universidad Andrés Bello. (2026a). *Apunte de la Fase 3: Núcleo algorítmico, eficiencia y programación orientada a objetos* [Material docente, MCDI500]. https://github.com/magistercienciadatos/Material_Didactico_Semana2

Universidad Andrés Bello. (2026b). *Apunte de la Fase 4: Consolidación del proyecto, visualización de datos y comunicación de resultados* [Material docente, MCDI500]. https://github.com/magistercienciadatos/Material_Didactico_Semana_3

Wilson, G., Bryan, J., Cranston, K., Kitzes, J., Nederbragt, L., & Teal, T. K. (2017). Good enough practices in scientific computing. *PLOS Computational Biology*, *13*(6), e1005510. https://doi.org/10.1371/journal.pcbi.1005510

**Declaración de uso de inteligencia artificial.** El equipo usó Claude (Anthropic), mediante Claude Code, para revisar código, escribir pruebas y preparar el borrador de este informe y el guion del video. El equipo tomó las decisiones, revisó el contenido y responde por él.
