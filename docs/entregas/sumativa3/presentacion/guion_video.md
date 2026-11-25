# Guion del video · Sumativa 3 · Grupo 7

> **Propuesta para revisión del grupo.** El reparto de tramos es una sugerencia: cámbienlo para que cada uno hable de lo que trabajó (la guía lo pide así y conecta con la coevaluación). Las cifras coinciden con el informe (`docs/entregas/sumativa3/`) y con las tablas de `F4/resultados/`.

## Requisitos de la guía (apartado 28)

- Entre **5 y 8 minutos**, subido a **Canvas Studio**. Meta: **7:00**, para tener margen.
- Hablan **los cuatro integrantes**.
- Debe tener apertura, contexto, metodología, resultados y conclusiones, con un hilo narrativo y buen manejo del tiempo.
- **No leer las diapositivas**: las frases de abajo son una guía y conviene decirlas con palabras propias.
- Debe haber **apoyo visual** en pantalla: diapositivas, el notebook ejecutándose y los gráficos.
- El video vale **12 puntos**, el criterio individual de mayor peso.

## Reparto propuesto

| Tramo | Quién | Diapositivas | Contenido |
|---|---|---|---|
| 0:00–0:35 | Jean | 1–2 | Apertura, integrantes y pregunta |
| 0:35–1:40 | Jairo | 3 | Contexto, datos y preparación (F2) |
| 1:40–2:55 | Pavel | 4–5 | Metodología, arquitectura y calidad del código |
| 2:55–3:35 | Jean | 6 | Demostración de reproducibilidad |
| 3:35–5:00 | Javier | 7–8 | Resultados 1 y 2 |
| 5:00–5:45 | Pavel | 9 | Resultado 3: Antofagasta |
| 5:45–6:20 | Jairo | 10 | Limitaciones |
| 6:20–7:00 | Jean | 11–12 | Conclusiones, mejoras y cierre |

Tiempo por persona: Jean ≈ 1:55, Jairo ≈ 1:40, Pavel ≈ 2:00, Javier ≈ 1:25. Si Javier trabajó más en las visualizaciones, puede tomar también el resultado 3.

---

## Tramo 1 · Jean · 0:00–0:35 · Diapositivas 1 y 2

**En pantalla:** portada y luego la pregunta.

**Idea:** presentar al grupo y plantear la pregunta en una frase. Dejar claro desde el inicio que se cuentan informes del CEN, no cortes a clientes.

> «Somos el grupo 7 de MCDI500: Jairo, Javier, Jean Paul y Pavel. Nos preguntamos qué tan expuestas están las 15 comunas más pobladas de Chile a las fallas del Sistema Eléctrico Nacional, según los informes que publica el Coordinador Eléctrico. Ojo con un punto: no medimos clientes sin luz ni SAIDI. Medimos exposición documentada, es decir, cuántos informes de falla nombran a cada comuna.»

## Tramo 2 · Jairo · 0:35–1:40 · Diapositiva 3

**En pantalla:** las cuatro cifras de los datos.

**Idea:** decir a quién le sirve el análisis, dar las cuatro cifras, explicar la tabla puente y cómo se trató el apagón.

> «Esto le sirve a los municipios, a la SEC y a quienes planifican la resiliencia de la red. Consolidamos 33 publicaciones mensuales del CEN, de enero de 2024 a septiembre de 2026: 18.019 registros con 40 variables. Los cruzamos con el Censo 2024 del INE y homologamos el 100 % de los vínculos con el código comunal. Un mismo informe puede nombrar varias comunas, así que armamos una tabla puente informe-comuna, para no contar cuatro informes donde había uno. El apagón del 25 de febrero de 2025 lo marcamos en F2 para poder analizarlo con y sin ese día.»

## Tramo 3 · Pavel · 1:40–2:55 · Diapositivas 4 y 5

**En pantalla:** las cuatro fases y luego la tabla de módulos.

**Idea:** decir una frase por fase. Explicar que cada fase lee lo que exportó la anterior y que F3 reproduce F2 byte a byte. Contar que el código está separado en un módulo por responsabilidad y que la eficiencia se midió.

> «Trabajamos en cuatro fases. En F1 definimos la pregunta y el entorno con dependencias de versión fija. En F2 preparamos los datos y exportamos siete CSV con su huella SHA-256. En F3 movimos el código a `src/`, y lo comprobamos así: F3 genera los mismos archivos que F2, byte a byte. En F4 agregamos la incertidumbre, la evolución mensual y la sensibilidad. Cada módulo de `src/` tiene una sola responsabilidad: si una causa viene mal escrita, se corrige en un único archivo, la tabla de equivalencias. Las clases aprenden de los datos de referencia, usan herencia y encapsulamiento, y el pipeline las recorre por polimorfismo. Tenemos 79 pruebas con casos normales, casos límite y excepciones. Medimos la eficiencia con `timeit` y `tracemalloc`: la versión vectorizada es entre 1,8 y 1,9 veces más rápida y baja la memoria de 8,3 a 5,3 MB. Antes de comparar, verificamos que las dos versiones dan el mismo resultado.»

## Tramo 4 · Jean · 2:55–3:35 · Diapositiva 6 + grabación de pantalla

**En pantalla:** una grabación acelerada de la pantalla.
- Clonar el repositorio.
- Instalar con `pip install -r requirements.txt`.
- En el notebook F4, ejecutar *Restart & Run All*.
- Correr `python -m unittest discover tests`, que debe terminar en **79 OK**.

Si la grabación se corta, volver a la diapositiva 6.

**Idea:** mostrar que, desde un clon limpio, todo corre de principio a fin y que ejecutar los notebooks no modifica archivos versionados.

## Tramo 5 · Javier · 3:35–5:00 · Diapositivas 7 y 8

**En pantalla:** la figura 506 (intervalos de confianza) y luego la 505 (mapa de calor mensual).

**Idea:** leer el ranking por grupos y no puesto por puesto, y mostrar que el apagón no explica el ranking. Seguir los tres pasos de cada hallazgo: qué muestra, qué se infiere y su límite.

> «Este gráfico muestra los informes por cada 100.000 habitantes al año, con su intervalo exacto de Poisson al 95 %. Solo Antofagasta se distingue con claridad: 45,6, con un intervalo entre 41,7 y 49,8 que no se superpone con ninguna otra comuna. En 13 de los 14 pares vecinos los intervalos sí se superponen, por eso el ranking se lee por grupos. Por ejemplo, Rancagua supera a Maipú, pero La Serena y Temuco no se pueden distinguir. Los rombos rojos muestran la frecuencia sin el día del apagón.
>
> En el mapa de calor, febrero de 2025 se enciende en las 15 comunas a la vez: 283 vínculos, 6,6 veces la mediana mensual. Aun así, si sacamos el 25 de febrero, el ranking cambia en un solo puesto: Viña del Mar y Puerto Montt intercambian el 11.º y el 12.º lugar. Antofagasta baja de 45,6 a 39,35 y sigue primera. La duración también tiene un límite: la mediana más alta, la de Valparaíso con 3,47 horas, no se distingue del resto. El límite de este análisis es que excluimos solo el día del apagón; los informes de los días cercanos se mantienen.»

## Tramo 6 · Pavel · 5:00–5:45 · Diapositiva 9

**En pantalla:** la figura 508 (sensibilidad a Antofagasta).

**Idea:** el liderazgo de Antofagasta es amplio y persistente, y no se debe a una sola instalación.

> «¿Antofagasta lidera por una sola subestación problemática? No. Sus informes se reparten en 85 subestaciones y 51 empresas, y las cinco más frecuentes reúnen solo el 46,5 %, la menor concentración de las 15 comunas. Además fue primera en 2024, en 2025 y en 2026. Tiene el 7,9 % de la población, pero el 28,2 % de los vínculos. Si la sacamos, la frecuencia agregada baja un 22,1 %, de 12,74 a 9,93. Por eso informamos las cifras conjuntas con y sin Antofagasta.»

## Tramo 7 · Jairo · 5:45–6:20 · Diapositiva 10

**En pantalla:** las cuatro tarjetas de limitaciones.

**Idea:** decir una frase por tarjeta. Las limitaciones también son resultado: dicen hasta dónde se puede afirmar cada cifra.

> «Cuatro límites. Uno: contamos informes, no clientes sin suministro. Dos: Poisson supone que los informes son independientes, y el apagón genera muchos al mismo tiempo. Tres: la duración se mide solo en los informes finalizados, y los pendientes podrían ser los más largos. Cuatro: 2026 tiene nueve meses, y la población de 2024 es un denominador de contexto, no un número de clientes.»

## Tramo 8 · Jean · 6:20–7:00 · Diapositivas 11 y 12

**En pantalla:** conclusiones y luego el cierre con el enlace al repositorio.

**Idea:** dar tres conclusiones y dos mejoras, cada una con su número. Hablar de asociaciones documentales, no de causas.

> «Concluimos tres cosas. Solo Antofagasta se distingue; el resto del ranking se lee por grupos. Los patrones comunales se mantienen: el apagón eleva todas las comunas, pero sin él el ranking casi no cambia. Y el liderazgo de Antofagasta es amplio y persistente. Proponemos dos mejoras: cruzar estos datos con los clientes afectados que informa la SEC, para pasar de informes a cortes, y revisar las desconexiones por instalaciones de terceros en Antofagasta, que son 110 informes de 25 empresas. Todo el código, los notebooks y las pruebas están en el repositorio. Gracias.»

Cortar la grabación cerca de los **7:00**.

---

## Antes de grabar

- [ ] El grupo revisa el reparto y cada uno ajusta su tramo a lo que trabajó.
- [ ] Cada uno ensaya su tramo **con cronómetro**.
- [ ] Jean graba antes la demostración de pantalla (tramo 4) y la acelera.
- [ ] Se graba en Canvas Studio con las diapositivas compartidas. Si cada uno graba por separado, se unen los tramos en orden.
- [ ] Se revisa que la duración total quede entre 5 y 8 minutos.
- [ ] Se pega el enlace del video en el apartado 28 del informe, donde hoy dice «[enlace pendiente]».

**Declaración de uso de IA:** las diapositivas y este guion los redactó Claude (Anthropic) como borrador, a partir de los resultados del repositorio. El grupo debe revisarlos, ajustarlos y decirlos con sus propias palabras.
