# ==========================================================
# MAGÍSTER EN CIENCIA DE DATOS E INTELIGENCIA ARTIFICIAL
# ASIGNATURA: MCDI500
# GRUPO 7
#
# CONSOLIDACIÓN HISTÓRICA DE INFORMES DE FALLAS
# SISTEMA ELÉCTRICO NACIONAL DE CHILE
# PERÍODO: 2024 - 2025 - 2026
# ==========================================================

from pathlib import Path
from zipfile import ZipFile, BadZipFile
import re
import pandas as pd


# ==========================================================
# 1. CONFIGURACIÓN DE DIRECTORIOS
# ==========================================================

RAIZ = Path(__file__).resolve().parent.parent

ENTRADA = RAIZ / "data" / "raw"

SALIDA = RAIZ / "data" / "processed"

DOCS = RAIZ / "docs"

SALIDA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)


# ==========================================================
# 2. IDENTIFICACIÓN DE ARCHIVOS DE FALLAS
# ==========================================================

# Buscar informes de fallas de 2024, 2025 y 2026.
# Se excluyen las tablas de desconexiones y limitaciones.

PATRON = re.compile(
    r"^(202[456])_(0[1-9]|1[0-2])_informe_fallas\.csv$",
    re.I
)

tablas = []
inventario = []
meses = set()


# ==========================================================
# 3. LECTURA AUTOMÁTICA DE TODOS LOS ZIP
# ==========================================================

for ruta_zip in sorted(ENTRADA.rglob("*.zip")):

    try:

        with ZipFile(ruta_zip) as z:

            archivos = [
                n for n in z.namelist()
                if PATRON.fullmatch(Path(n).name)
            ]

            for nombre in archivos:

                coincidencia = PATRON.fullmatch(
                    Path(nombre).name
                )

                anio, mes = map(
                    int,
                    coincidencia.groups()
                )

                # Evitar cargar dos veces un mismo mes.

                if (anio, mes) in meses:

                    raise ValueError(
                        f"El período {anio}-{mes:02d} "
                        f"está duplicado. Revisa {ruta_zip.name}"
                    )

                # Leer el CSV directamente desde el ZIP.

                with z.open(nombre) as origen:

                    try:

                        df = pd.read_csv(
                            origen,
                            encoding="utf-8-sig",
                            dtype="string"
                        )

                    except UnicodeDecodeError:

                        origen.seek(0)

                        df = pd.read_csv(
                            origen,
                            encoding="latin-1",
                            dtype="string"
                        )

                df.columns = df.columns.str.strip()

                # Verificar columnas esenciales.

                esenciales = {
                    "Número",
                    "Fecha Perturbación",
                    "Fecha Efectiva Fin"
                }

                faltan = esenciales - set(df.columns)

                if faltan:

                    raise ValueError(
                        f"{nombre}: faltan columnas "
                        f"{sorted(faltan)}"
                    )

                # Registrar trazabilidad.

                df["anio_publicacion"] = anio

                df["mes_publicacion"] = mes

                df["archivo_zip"] = ruta_zip.name

                df["archivo_csv"] = Path(nombre).name

                df["fila_fuente"] = range(
                    2,
                    len(df) + 2
                )

                tablas.append(df)

                inventario.append({

                    "anio_publicacion": anio,
                    "mes_publicacion": mes,
                    "archivo_zip": ruta_zip.name,
                    "registros": len(df),
                    "columnas": len(df.columns) - 5

                })

                meses.add((anio, mes))

                print(
                    f"OK {anio}-{mes:02d}: "
                    f"{len(df):,} registros"
                )

    except BadZipFile:

        raise SystemExit(
            f"Archivo ZIP dañado: {ruta_zip}"
        )


# ==========================================================
# 4. VERIFICAR QUE EXISTAN DATOS
# ==========================================================

if not tablas:

    raise SystemExit(
        "No se encontraron informes de fallas "
        "dentro de los ZIP de data/raw."
    )


# ==========================================================
# 5. CONSOLIDAR PUBLICACIONES
# ==========================================================

publicaciones = pd.concat(
    tablas,
    ignore_index=True,
    sort=False
)

# Normalizar identificadores de fallas.

publicaciones["id_falla"] = (
    publicaciones["Número"]
    .str.strip()
    .str.replace(
        r"\.0+$",
        "",
        regex=True
    )
)

publicaciones.loc[
    publicaciones["id_falla"].eq(""),
    "id_falla"
] = pd.NA

# Guardar todos los registros publicados.

publicaciones.to_csv(
    SALIDA / "cen_fallas_2024_2026_publicaciones.csv",
    index=False,
    encoding="utf-8-sig"
)


# ==========================================================
# 6. IDENTIFICAR EVENTOS REPETIDOS
# ==========================================================

con_id = publicaciones.loc[
    publicaciones["id_falla"].notna()
].copy()

sin_id = publicaciones.loc[
    publicaciones["id_falla"].isna()
].copy()

# Ordenar cronológicamente las publicaciones.

con_id = con_id.sort_values(
    ["anio_publicacion", "mes_publicacion"],
    kind="stable"
)

# Conservar la última versión publicada de cada falla.

ultimas = con_id.drop_duplicates(
    subset="id_falla",
    keep="last"
)

# Conservar registros sin identificador para revisión.

eventos = pd.concat(
    [ultimas, sin_id],
    ignore_index=True,
    sort=False
)


# ==========================================================
# 7. PROCESAR FECHAS DE LOS EVENTOS
# ==========================================================

# Convertir las fechas a una referencia temporal uniforme.
# UTC permite procesar registros con diferentes zonas horarias.

inicio = pd.to_datetime(
    eventos["Fecha Perturbación"],
    errors="coerce",
    format="mixed",
    utc=True
)

fin = pd.to_datetime(
    eventos["Fecha Efectiva Fin"],
    errors="coerce",
    format="mixed",
    utc=True
)

eventos["anio_evento"] = inicio.dt.year

eventos["mes_evento"] = inicio.dt.month


# ==========================================================
# 8. CALCULAR DURACIÓN REGISTRADA
# ==========================================================

horas = (
    fin - inicio
).dt.total_seconds() / 3600

# Identificar intervalos negativos.

eventos["intervalo_negativo"] = (
    horas.lt(0).fillna(False)
)

# No utilizar intervalos negativos como duraciones válidas.

eventos["duracion_horas"] = (
    horas.where(horas.ge(0)).round(3)
)

# Identificar registros con fechas inválidas.

eventos["fecha_invalida_o_ausente"] = (
    inicio.isna()
)

# Identificar eventos fuera del período de estudio.

eventos["fuera_de_periodo"] = (
    ~eventos["anio_evento"].isin(
        [2024, 2025, 2026]
    )
)


# ==========================================================
# 9. GUARDAR BASE HISTÓRICA CONSOLIDADA
# ==========================================================

eventos.to_csv(
    SALIDA / "cen_fallas_2024_2026_eventos.csv",
    index=False,
    encoding="utf-8-sig"
)

# Guardar inventario de fuentes.

pd.DataFrame(inventario).sort_values(
    ["anio_publicacion", "mes_publicacion"]
).to_csv(
    DOCS / "inventario_fallas_2024_2026.csv",
    index=False,
    encoding="utf-8-sig"
)


# ==========================================================
# 10. GENERAR INFORME EN TERMINAL
# ==========================================================

print("\n==========================================")
print("RESUMEN DE CONSOLIDACIÓN HISTÓRICA")
print("==========================================")

print("Meses procesados:", len(meses))

for anio in [2024, 2025, 2026]:

    presentes = sorted(
        m for y, m in meses if y == anio
    )

    print(
        f"\nAño {anio} - Meses encontrados:",
        presentes
    )

    # Para 2024 y 2025 buscamos años completos.

    if anio in (2024, 2025):

        pendientes = sorted(
            set(range(1, 13)) - set(presentes)
        )

        if pendientes:

            print(
                f"AVISO: faltan meses de {anio}:",
                pendientes
            )

print("\nRegistros publicados:", len(publicaciones))

print(
    "Registros repetidos por identificador:",
    len(con_id) - len(ultimas)
)

print(
    "Registros sin identificador:",
    len(sin_id)
)

print(
    "Eventos consolidados:",
    len(eventos)
)

print(
    "Eventos con duración válida:",
    eventos["duracion_horas"].notna().sum()
)

print(
    "Eventos con intervalo negativo:",
    eventos["intervalo_negativo"].sum()
)

print("\nEVENTOS SEGÚN AÑO DE OCURRENCIA")

print(
    eventos["anio_evento"]
    .value_counts(dropna=False)
    .sort_index()
)

print("\nCONSOLIDACIÓN FINALIZADA CORRECTAMENTE")