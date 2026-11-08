# Proyecto MCDI500 — Grupo 7

## Exposición operacional documentada de las 15 comunas más pobladas de Chile a las fallas del SEN (2024–2026)

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
| **F1** | Planteamiento territorial, objetivos, verificación del entorno, pruebas y mapa conceptual | **Desarrollada** · corre completa con *Restart & Run All* |
| **F2** | Obtención, exploración, limpieza, homologación INE (100 %), transformación y 40 pruebas | **Desarrollada** · exporta 7 CSV con SHA-256 a `data/processed/f2/` |
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
│   ├── descargar_cen.py             # paso 0: descarga los 33 ZIP del CEN a data/raw/
│   ├── consolidar_fallas_2024_2026.py  # paso 1: ZIP → data/processed/
│   └── trazabilidad.py              # entorno, versiones, commit y semilla (lo usan F1 y F2)
├── docs/
│   ├── fuente_dataset.md            # procedencia de las fuentes CEN e INE
│   ├── decisiones.md                # registro de decisiones (D-01 a D-09)
│   ├── diccionario_variables.csv    # rol y decisión de las 28 variables originales
│   ├── verificacion_entorno.md      # registro de ejecuciones en un segundo equipo
│   ├── descargas_cen.csv            # URL, SHA-256 y fecha de cada ZIP descargado
│   ├── mapa_conceptual_F1_impacto_comunal.png  # Generado ejecutando F1
│   └── entregas/
│       ├── formativa1/              # PDF entregado en la Formativa 1
│       └── sumativa1/               # informe técnico (fuente .md, generador y PDF)
├── data/
│   ├── raw/                         # ZIP mensuales CEN: NO se versionan (ver data/raw/README.md)
│   ├── external/                    # Censo 2024 INE (ver data/external/README.md)
│   ├── reference/                   # Tablas de equivalencias CEN↔INE (las lee F2)
│   └── processed/                   # SÍ se versiona: lo leen F1 y F2
│       ├── cen_fallas_2024_2026_eventos.csv        # un registro por id_falla
│       ├── cen_fallas_2024_2026_publicaciones.csv  # todas las filas publicadas
│       ├── f2/                      # salidas de F2 + manifest_f2.json (SHA-256)
│       └── homologacion/            # nombres homologados por equivalencia / no homologados
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
5. *(Opcional)* Reconstruir los consolidados **desde la fuente original**:

   ```bash
   python src/descargar_cen.py                 # 33 ZIP (~80 MB) → data/raw/ y docs/descargas_cen.csv
   python src/consolidar_fallas_2024_2026.py   # data/raw/ → data/processed/
   ```

   El 2026-11-08 esta reconstrucción dio un contenido idéntico al versionado (ver `docs/fuente_dataset.md`). El Excel del INE ya viene en `data/external/`; su origen y su SHA-256 están en `data/external/README.md`.

### Informe técnico (Sumativa 1)

El texto del informe se edita **solo** en `docs/entregas/sumativa1/informe_sumativa1.md`. El PDF (`mcdi500_s1_grupo7.pdf`) se genera con un script que hace lo siguiente:

- arma la portada institucional y el índice automático;
- usa tamaño carta y Arial 11 pt;
- calcula desde Git los commits por integrante;
- verifica que ningún texto quede bajo 11 pt.

```bash
python -m pip install -r docs/entregas/sumativa1/requirements-informe.txt   # reportlab y pypdf
python docs/entregas/sumativa1/generar_informe.py
```

Estas dos dependencias están separadas de `requirements.txt` porque los notebooks no las usan.

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
