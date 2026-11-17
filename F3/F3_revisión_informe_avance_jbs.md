Revisión Informe Avance F3 17-11-2026
 Autor: Jairo Barraza S.
 ** Observación 1: Archivo F2
 En F2 el archivo 04_cen_fallas_comunas_integrado.csv  la columna "clave_ine_propuesta" viene vacía.¿ Debería corresponder a la columna "código_comuna" del archivo 05_cen_perfiles_15_comunas.csv ?

 ** Observación 2: Informe Avance F3. En II.b 
- la columna Objetivo fue contrastada con la tabla F1 del 5.3 Correspondencia de objetivos, productos y etapas. En la tabla del Informe de Avance no se incluye  el OE1 en II.b , pero aunque la transformación "Normalizar por población" fue clasificada bajo OE4 por su contribución a los indicadores de exposición operacional. 
- También se podría incluir el OE1 (Integración CEN–INE) en la tabla del Informe de Avance, dado que se combina el conteo de informes no anulados provenientes del CEN con la población censada 2024 proveniente del INE para construir el indicador frecuencia_100k_hab_anio en esta F3.


** Observación 3: Informe Avance F3. En II.c Validación técnica y verificación:
 -  Revisadas las pruebas automatizadas, en el archivo test_componentes_f3.py = 20 y test_consolidar.py =  15 , total 35. Correcto, concuerda con texto informe.

- En notebook F3, en sección 9.5 se indican 13 pruebas  POO correctas y 15 pruebas integrales , concuerda con el texto.

Equivalencia con la Fase 2:
 - Vínculos homolagos 02_cen_asociaciones_auditadas.csv (F2), se indica 23.284 fila x 8 columnas. Mi revisión indica que son 12 columnas. 

- Tasa del NormalizadorPoblacional. El valor calculado 2,75 se aplica correctamente en las 15 comunas para calcular frecuencia_100k_hab_anio en el archivo F3_701_Panel_Integrado_Comunal.csv.

 - Script de consolidación reorganizado frente a los consolidados versionados. En 6.16.7 Validación Técnica del procesamiento se señala " Los consolidados del CEN también se reconstruyeron desde la fuente original: se descargaron de nuevo los 33 ZIP con src/descargar_cen.py y el contenido resultó idéntico (docs/fuente_dataset.md). Esto no reemplaza una auditoría independiente de las fuentes". Comentario: el texto no explica exactamente cómo se comprobó que el resultado era idéntico. No sabemos si la comparación fue mediante:pd.testing.assert_frame_equal(...), ó, assert sha256_original == sha256_reconstruido, ó, assert len(df_original) == len(df_reconstruido).El informe afirma el resultado, pero no muestra todavía el mecanismo.

** Observación 4: Informe Avance F3.II.d. Eficiencia y optimización.
- En 5.2.5. Criterios de comparación, se basa en relacion_recursivo_iterativo (A/B)

 - A. Recursiva vs B. Iterativa con pila .  B un 4,4 % más rápida en la escala mayor (61.280 asociaciones); más rápida en 5 de 6 escalas

Revisión: en los tiempos observados, algoritmo Iterativo gana en 5 de 6 escalas. En la escala máxima (32): A.Recursivo = 0,23054 ms , B.Iterativo = 0,21639 ms. Diferencia:0,23054 (A) - 0,21639 (B) = 0,01415 y en porcentaje = 0,01415 / 0,23054 = 0,0614 x 100 % = 6,1% más rápida B.

  - Uso de memoria. Revisar comentario uso de memoria. La tabla de 5.2.6 indica que B. Iterativo consume menos memoria (KB) que A. Recursiva en 5 de 6 Factores de Escala. Actual redacción señala "La versión iterativa gana en tiempo, gasta levemente más memoria ...."
