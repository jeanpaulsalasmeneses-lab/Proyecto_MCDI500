# data/raw — datos originales del CEN

Esta carpeta guarda los **datos originales, que nunca se modifican**. Su contenido no se sube a GitHub (ver `.gitignore`): solo se versiona este README.

## Qué va aquí

Los 33 ZIP mensuales de "Desconexiones e intervenciones" publicados por el Coordinador Eléctrico Nacional (CEN), de enero de 2024 a septiembre de 2026:

```text
data/raw/
├── 2024_01_conexiones_intervenciones.zip
├── 2024_02_conexiones_intervenciones.zip
├── ...
└── 2026_09_conexiones_intervenciones.zip
```

La lista completa, con el número de registros de cada ZIP, está en `docs/inventario_fallas_2024_2026.csv`.

## De dónde se descargan

Coordinador Eléctrico Nacional, *Desconexiones e intervenciones / informes de falla / limitaciones*:
https://www.coordinador.cl/operacion/graficos/desconexiones-e-intervenciones/

La página muestra una tabla con las columnas Año, Mes y Descarga, con un enlace «Descargar» por mes. Cada enlace apunta a un ZIP con este patrón:

```text
https://cen-datalake-public.s3.amazonaws.com/conexiones_intervenciones/AAAA/MM/AAAA_MM_conexiones_intervenciones.zip
```

Cada ZIP trae tres CSV: solicitudes de trabajo, limitaciones e **informe de fallas**. Solo se usa el último.

### Opción A: script (recomendada)

Desde la raíz del proyecto, con el entorno virtual activo:

```bash
python src/descargar_cen.py
```

- Descarga los 33 ZIP (~80 MB, 1 a 2 minutos).
- Verifica que cada ZIP esté sano y traiga el informe de fallas.
- No vuelve a descargar los que ya existen; para forzar la descarga, usar `--forzar`.
- Escribe `docs/descargas_cen.csv` con la URL, el tamaño, el SHA-256, la fecha de publicación del CEN y la fecha de descarga de cada archivo. Ese registro sí se versiona: es la evidencia de **qué versión** de los datos se usó.

### Opción B: manual

1. Abrir la página del CEN indicada arriba.
2. En la tabla, usar **Descargar** en cada mes desde enero de 2024 hasta septiembre de 2026.
3. Guardar los 33 ZIP en esta carpeta **sin cambiarles el nombre** (`AAAA_MM_conexiones_intervenciones.zip`).

## Cómo se procesan

Desde la raíz del proyecto, con el entorno virtual activo:

```bash
python src/consolidar_fallas_2024_2026.py
```

El script lee **solo** el CSV `AAAA_MM_informe_fallas.csv` que viene dentro de cada ZIP y escribe en `data/processed/`:

- `cen_fallas_2024_2026_publicaciones.csv`: todas las filas publicadas, con su procedencia (`archivo_zip`, `archivo_csv`, `fila_fuente`).
- `cen_fallas_2024_2026_eventos.csv`: un registro por `id_falla`, con columnas derivadas (`duracion_horas`, `fuera_de_periodo`, etc.).

No hace falta descargar los ZIP para ejecutar F1 y F2: los dos consolidados ya están versionados en `data/processed/`. Los ZIP solo se necesitan para reconstruir esos archivos desde la fuente original.
