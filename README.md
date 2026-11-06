# Proyecto MCDI500 — Grupo 7

## Análisis del impacto operacional documentado de las fallas del SEN sobre comunas prioritarias de Chile

**Curso:** Programación para la Ciencia de Datos · Magíster en Ciencia de Datos e Inteligencia Artificial · UNAB  
**Grupo 7:** Jairo Barraza Salazar · Javier Huamanni Barrera · Jean Salas Meneses · Pavel Chávez San Martín

### Propósito y pregunta

Caracterizar la **exposición operacional documentada** en las **15 comunas con mayor población censada del país según Censo 2024**, vinculando los informes de falla del Coordinador Eléctrico Nacional (CEN) con antecedentes territoriales del Instituto Nacional de Estadísticas (INE). Se analizarán la frecuencia y recurrencia de los informes que mencionan una comuna, las categorías de consumo reportado y las duraciones documentales técnicamente válidas.

**No se identifican automáticamente usuarios sin suministro.** Un informe puede mencionar varias comunas y no necesariamente implicar corte de suministro. No se calculan SAIDI/SAIFI a partir del CSV de fallas: esos indicadores requieren cantidad de clientes efectivamente interrumpidos y sus tiempos de corte.

### Datos y criterio territorial

- **CEN:** 33 publicaciones mensuales (enero 2024–septiembre 2026). El consolidado inicial contiene 18.019 registros y 40 variables. Variables fundamentales: `Número`, `id_falla`, `Comuna`, `Zona Afectada`, `Consumo`, `Estado`, `Fecha Perturbación` y `Fecha Efectiva Fin`.
- **INE:** resultados oficiales del Censo 2024 a escala comunal. Selección programada de las **15 comunas más pobladas**, una vez cargada una tabla oficial con nombre, región, código y población. La selección no se realiza por cantidad de fallas.
- **SEC:** indicador SAIDI solo como **contexto externo**, sin asumir correspondencia uno a uno entre los informes CEN y las interrupciones de distribución.

**Interpretación:** `Comuna` puede contener valores múltiples separados por `|`. La etapa F2 debe generar una tabla puente (`id_falla`, `codigo_comuna`) sin multiplicar el número nacional de informes únicos. `consumo_no_afectado` no se considera afectación reportada.

### Estado por fase

| Fase | Alcance | Estado |
|---|---|---|
| **F1** | Planteamiento territorial, objetivos, verificación de campos, pruebas y mapa conceptual | Notebook reformulado; **requiere ejecución con datos locales** |
| **F2** | Exploración, limpieza, códigos comunales INE, tabla informe–comuna y validación | **Pendiente de implementación** |
| **F3** | Indicadores comunales y comparaciones por período, consumo, causa y duración | Proyectado |
| **F4** | Visualizaciones, informe, conclusiones y límites de inferencia | Proyectado |

### Archivos y organización

```text
Proyecto_MCDI500/
├── F1/
│   └── F1_Definición.ipynb
├── F2/
│   └── F2_Exploracion_y_Preprocesamiento.ipynb
├── src/
│   └── consolidar_fallas_2024_2026.py
├── docs/
│   └── mapa_conceptual_F1_impacto_comunal.png  # Generado ejecutando F1
├── data/
│   ├── raw/                         # ZIP mensuales CEN: NO se versionan (ver data/raw/README.md)
│   ├── processed/                   # SÍ se versiona: lo leen F1 y F2
│   │   ├── cen_fallas_2024_2026_eventos.csv        # un registro por id_falla
│   │   └── cen_fallas_2024_2026_publicaciones.csv  # todas las filas publicadas
│   └── external/                    # Fuente comunal INE (F2)
├── requirements.txt
└── README.md
```

### Ejecución local

Los consolidados del CEN ya vienen en `data/processed/`, así que basta con clonar, crear el entorno y ejecutar los notebooks. El proyecto se probó con **Python 3.13**.

1. Clonar el repositorio y abrir la carpeta en Visual Studio Code.
2. Crear y activar el entorno virtual e instalar las dependencias.

   **Windows (PowerShell):**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

   **Linux / macOS (bash o zsh):**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

   `pywinpty` solo se instala en Windows; en Linux y macOS pip lo omite automáticamente.

3. Abrir `F1/F1_Definición.ipynb`, seleccionar el kernel `.venv` y usar **Restart Kernel and Run All Cells**. La figura del mapa conceptual se genera en `docs/`.
4. Repetir con `F2/F2_Exploracion_y_Preprocesamiento.ipynb`.
5. *(Opcional)* Reconstruir los consolidados desde la fuente original: descargar los 33 ZIP del CEN en `data/raw/` (ver `data/raw/README.md`) y ejecutar `python src/consolidar_fallas_2024_2026.py`.
6. La descarga de la tabla INE, la homologación territorial y la preparación de resultados se desarrollarán en F2. **No hay resultados comunales finales hasta su validación**.

### Criterios de calidad

- Conservar `id_falla` y procedencia documental, diferenciar ocurrencia y publicación.
- Exponer cobertura de `Comuna` y categoría de `Consumo`.
- Separar valores multicomuna sin contar cuatro informes donde había uno.
- Validar nombres comunales con código oficial INE; reportar no homologados.
- Comparar enero–septiembre en 2024, 2025 y 2026 cuando se incluyan los tres años.
- Evitar llamar **horas de corte**, **impacto en clientes** o **SAIDI** a la duración registrada de informes de falla.
- Versionar decisiones y contribuciones en GitHub.

### Fuentes principales

- CEN: https://www.coordinador.cl/operacion/graficos/desconexiones-e-intervenciones/
- INE Censo 2024: https://censo2024.ine.gob.cl/resultados/
- CNE calidad de distribución: https://www.cne.cl/normativas/electrica/normas-tecnicas/ntcsdx2024/
- SEC SAIDI: https://www.sec.cl/informe-sec-saidi/

**Pendiente de la rúbrica:** agregar dos fuentes docentes reales de la asignatura, incorporar las citas pertinentes y presentar el PDF institucional integrado F1–F2.
