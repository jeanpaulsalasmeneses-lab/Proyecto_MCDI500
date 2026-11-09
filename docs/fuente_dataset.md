# Procedencia y delimitación del dataset — MCDI500

## 1. Identificación de fuentes oficiales

### Fuente primaria: Coordinador Eléctrico Nacional (CEN)
* **Organismo:** Coordinador Eléctrico Nacional (organismo técnico e independiente encargado de coordinar la operación del Sistema Eléctrico Nacional, SEN).
* **Portal oficial:** [CEN - Desconexiones e Intervenciones](https://www.coordinador.cl/operacion/graficos/desconexiones-e-intervenciones/)
* **Intervalo temporal:** Enero 2024 a Septiembre 2026 (33 publicaciones mensuales consolidadas).
* **Archivos procesados:** `data/processed/cen_fallas_2024_2026_eventos.csv` (18.019 registros únicos por falla, 40 variables) y `cen_fallas_2024_2026_publicaciones.csv`.
* **Variables fundamentales:** `id_falla`, `Comuna`, `Zona Afectada`, `Consumo`, `Estado`, `Causa Definitiva`, `Fecha Perturbación` y `Fecha Efectiva Fin`.

### Fuente secundaria: Instituto Nacional de Estadísticas (INE)
* **Organismo:** Instituto Nacional de Estadísticas de Chile.
* **Portal oficial:** [Resultados Oficiales Censo 2024](https://censo2024.ine.gob.cl/resultados/)
* **Criterio de selección territorial:** Selección algorítmica de las **15 comunas con mayor población censada del país**. La selección es estrictamente poblacional (demográfica), no condicionada a la cantidad de fallas reportadas.
* **Archivo de referencia:** `data/external/ine_censo2024_poblacion_comunal.xlsx`.

---

## 2. Tratamiento de datos y advertencias metodológicas

1. **Exposición operacional vs. Cortes de suministro:**
   * La mención de una comuna en un informe del CEN documenta una **afectación o contingencia operacional** en la infraestructura de transporte o distribución.
   * **No equivale automáticamente a un corte de suministro en clientes finales.** Los indicadores de continuidad (SAIDI/SAIFI) de la SEC y CNE requieren contabilizar clientes interrumpidos y tiempos efectivos de corte domiciliario, datos que no forman parte del reporte de eventos del CEN.

2. **Tratamiento multicomuna:**
   * La variable `Comuna` en el dataset CEN puede reportar múltiples comunas separadas por el delimitador `|` (por ejemplo, en líneas de transmisión que cruzan límites interurbanos).
   * En la etapa F2 se construye una relación puente informe–comuna que no multiplica artificialmente el conteo nacional de fallas únicas.

3. **Validez técnica de duraciones:**
   * La duración se calcula únicamente a partir de informes cerrados que poseen tanto `Fecha Perturbación` como `Fecha Efectiva Fin`. Aquellos reportes con estado abierto o en investigación se analizan por separado en el perfil de completitud.

---

## 3. Consideraciones éticas, privacidad y gobernanza

* **Naturaleza de los datos:** Son datos abiertos de infraestructura pública regulada.
* **Privacidad:** No se procesa información personal sensible, nombres, RUTs ni domicilios particulares de consumidores.
* **Reproducibilidad:** Los scripts y notebooks del repositorio permiten regenerar todo el procesamiento desde los archivos fuente mediante dependencias abiertas documentadas en `requirements.txt`.