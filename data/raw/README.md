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

## Cómo se procesan

Desde la raíz del proyecto, con el entorno virtual activo:

```bash
python src/consolidar_fallas_2024_2026.py
```

El script lee **solo** el CSV `AAAA_MM_informe_fallas.csv` que viene dentro de cada ZIP y escribe en `data/processed/`:

- `cen_fallas_2024_2026_publicaciones.csv`: todas las filas publicadas, con su procedencia (`archivo_zip`, `archivo_csv`, `fila_fuente`).
- `cen_fallas_2024_2026_eventos.csv`: un registro por `id_falla`, con columnas derivadas (`duracion_horas`, `fuera_de_periodo`, etc.).

No hace falta descargar los ZIP para ejecutar F1 y F2: los dos consolidados ya están versionados en `data/processed/`. Los ZIP solo se necesitan para reconstruir esos archivos desde la fuente original.
