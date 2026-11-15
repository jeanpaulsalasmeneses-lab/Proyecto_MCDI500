# ==========================================================
# MAGÍSTER EN CIENCIA DE DATOS E INTELIGENCIA ARTIFICIAL
# ASIGNATURA: MCDI500
# GRUPO 7
#
# CONSOLIDACIÓN HISTÓRICA DE INFORMES DE FALLAS
# SISTEMA ELÉCTRICO NACIONAL DE CHILE
# PERÍODO: 2024 - 2025 - 2026
# ==========================================================
"""
Consolida los informes de falla del CEN publicados en 33 ZIP mensuales.

Flujo (cada paso es una función con un solo propósito):

    ZIP de data/raw/
      -> leer_zip()                      lee solo AAAA_MM_informe_fallas.csv
         -> leer_csv_publicado()         UTF-8 con BOM, o latin-1 como respaldo
         -> validar_estructura()         columnas esenciales presentes
         -> agregar_trazabilidad()       año, mes, ZIP, CSV y fila de origen
      -> cargar_publicaciones()          los 33 meses, sin períodos repetidos
      -> consolidar_publicaciones()      une las tablas y normaliza id_falla
      -> seleccionar_ultima_version()    un registro por id_falla
      -> derivar_variables_temporales()  fechas en UTC, duración y validaciones
      -> exportar_csv()                  data/processed/ y docs/

Uso, desde la raíz del proyecto:

    python src/consolidar_fallas_2024_2026.py
    python src/consolidar_fallas_2024_2026.py --entrada data/raw --salida /tmp/prueba

Las funciones se prueban en tests/test_consolidar.py
(python -m unittest discover tests).
"""

import argparse
import io
import re
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import pandas as pd


# ==========================================================
# 1. CONFIGURACIÓN
# ==========================================================

RAIZ = Path(__file__).resolve().parent.parent

# Solo los informes de fallas de 2024, 2025 y 2026. Se excluyen las
# tablas de desconexiones y limitaciones que vienen en el mismo ZIP.
PATRON_INFORME = re.compile(
    r"^(202[456])_(0[1-9]|1[0-2])_informe_fallas\.csv$",
    re.I
)

COLUMNAS_ESENCIALES = frozenset({
    "Número",
    "Fecha Perturbación",
    "Fecha Efectiva Fin",
})

COLUMNAS_TRAZABILIDAD = (
    "anio_publicacion",
    "mes_publicacion",
    "archivo_zip",
    "archivo_csv",
    "fila_fuente",
)

ANIOS_ESTUDIO = (2024, 2025, 2026)


class ErrorConsolidacion(Exception):
    """Error de datos de entrada que impide consolidar."""


# ==========================================================
# 2. LECTURA Y VALIDACIÓN DE CADA PUBLICACIÓN
# ==========================================================

def periodo_desde_nombre(nombre_archivo):
    """
    Devuelve (año, mes) si el archivo es un informe de fallas, o None.

    >>> periodo_desde_nombre("carpeta/2025_03_informe_fallas.csv")
    (2025, 3)
    """
    coincidencia = PATRON_INFORME.fullmatch(Path(nombre_archivo).name)
    if coincidencia is None:
        return None
    anio, mes = coincidencia.groups()
    return int(anio), int(mes)


def leer_csv_publicado(contenido):
    """
    Lee un CSV del CEN (bytes) como texto, sin convertir tipos.

    Usa UTF-8 con BOM y, si falla, latin-1 (algunas publicaciones antiguas).
    """
    try:
        return pd.read_csv(io.BytesIO(contenido), encoding="utf-8-sig", dtype="string")
    except UnicodeDecodeError:
        return pd.read_csv(io.BytesIO(contenido), encoding="latin-1", dtype="string")


def validar_estructura(df, nombre_archivo, esenciales=COLUMNAS_ESENCIALES):
    """
    Limpia los espacios de los nombres de columna y exige las esenciales.

    Devuelve una copia; no modifica df.
    """
    salida = df.copy()
    salida.columns = salida.columns.str.strip()
    faltan = set(esenciales) - set(salida.columns)
    if faltan:
        raise ErrorConsolidacion(f"{nombre_archivo}: faltan columnas {sorted(faltan)}")
    return salida


def agregar_trazabilidad(df, anio, mes, archivo_zip, archivo_csv):
    """
    Agrega la procedencia de cada fila: año y mes de publicación, ZIP, CSV
    y número de fila en el CSV original (la fila 1 es el encabezado).
    """
    salida = df.copy()
    salida["anio_publicacion"] = anio
    salida["mes_publicacion"] = mes
    salida["archivo_zip"] = archivo_zip
    salida["archivo_csv"] = archivo_csv
    salida["fila_fuente"] = range(2, len(salida) + 2)
    return salida


def leer_zip(ruta_zip):
    """
    Lee los informes de fallas de un ZIP.

    Devuelve una lista de tuplas (año, mes, tabla con trazabilidad).
    Lanza ErrorConsolidacion si el ZIP está dañado.
    """
    ruta_zip = Path(ruta_zip)
    try:
        with ZipFile(ruta_zip) as archivo:
            informes = []
            for nombre in archivo.namelist():
                periodo = periodo_desde_nombre(nombre)
                if periodo is None:
                    continue
                anio, mes = periodo
                tabla = leer_csv_publicado(archivo.read(nombre))
                tabla = validar_estructura(tabla, nombre)
                tabla = agregar_trazabilidad(tabla, anio, mes, ruta_zip.name, Path(nombre).name)
                informes.append((anio, mes, tabla))
            return informes
    except BadZipFile as error:
        raise ErrorConsolidacion(f"Archivo ZIP dañado: {ruta_zip}") from error


def cargar_publicaciones(entrada, informar=print):
    """
    Lee todos los ZIP de la carpeta de entrada, en orden alfabético.

    Devuelve (tablas, inventario, meses):
    - tablas: lista de DataFrames, uno por publicación mensual;
    - inventario: DataFrame con año, mes, ZIP, registros y columnas originales;
    - meses: conjunto de (año, mes) cargados.
    Lanza ErrorConsolidacion si un mes aparece dos veces o no hay informes.
    """
    tablas, inventario, meses = [], [], set()
    for ruta_zip in sorted(Path(entrada).rglob("*.zip")):
        for anio, mes, tabla in leer_zip(ruta_zip):
            if (anio, mes) in meses:
                raise ErrorConsolidacion(
                    f"El período {anio}-{mes:02d} está duplicado. Revisa {ruta_zip.name}"
                )
            meses.add((anio, mes))
            tablas.append(tabla)
            inventario.append({
                "anio_publicacion": anio,
                "mes_publicacion": mes,
                "archivo_zip": ruta_zip.name,
                "registros": len(tabla),
                "columnas": len(tabla.columns) - len(COLUMNAS_TRAZABILIDAD),
            })
            informar(f"OK {anio}-{mes:02d}: {len(tabla):,} registros")

    if not tablas:
        raise ErrorConsolidacion(f"No se encontraron informes de fallas dentro de los ZIP de {entrada}.")

    inventario = (
        pd.DataFrame(inventario)
        .sort_values(["anio_publicacion", "mes_publicacion"])
        .reset_index(drop=True)
    )
    return tablas, inventario, meses


# ==========================================================
# 3. CONSOLIDACIÓN
# ==========================================================

def normalizar_id_falla(numero):
    """
    Convierte el campo Número en un identificador de texto.

    Quita espacios y el sufijo decimal que deja Excel ("2024000001.0" ->
    "2024000001"). Los vacíos quedan como NA.
    """
    identificador = numero.str.strip().str.replace(r"\.0+$", "", regex=True)
    return identificador.mask(identificador.eq(""), pd.NA)


def consolidar_publicaciones(tablas):
    """Une las publicaciones mensuales y agrega la columna id_falla."""
    publicaciones = pd.concat(tablas, ignore_index=True, sort=False)
    publicaciones["id_falla"] = normalizar_id_falla(publicaciones["Número"])
    return publicaciones


def seleccionar_ultima_version(publicaciones):
    """
    Deja un registro por id_falla: la última versión publicada.

    Los registros sin identificador se conservan al final, para revisarlos.
    Devuelve (eventos, repetidos, sin_identificador).
    """
    con_id = publicaciones.loc[publicaciones["id_falla"].notna()].sort_values(
        ["anio_publicacion", "mes_publicacion"], kind="stable"
    )
    sin_id = publicaciones.loc[publicaciones["id_falla"].isna()]
    ultimas = con_id.drop_duplicates(subset="id_falla", keep="last")
    eventos = pd.concat([ultimas, sin_id], ignore_index=True, sort=False)
    return eventos, len(con_id) - len(ultimas), len(sin_id)


def derivar_variables_temporales(eventos, anios_estudio=ANIOS_ESTUDIO):
    """
    Agrega variables temporales sin modificar las columnas originales.

    - Fechas en UTC (las publicaciones mezclan zonas horarias).
    - anio_evento y mes_evento, según la fecha de perturbación.
    - duracion_horas: término - inicio, solo si no es negativa.
    - intervalo_negativo, fecha_invalida_o_ausente y fuera_de_periodo.
    """
    salida = eventos.copy()
    inicio = pd.to_datetime(salida["Fecha Perturbación"], errors="coerce", format="mixed", utc=True)
    fin = pd.to_datetime(salida["Fecha Efectiva Fin"], errors="coerce", format="mixed", utc=True)

    salida["anio_evento"] = inicio.dt.year
    salida["mes_evento"] = inicio.dt.month

    horas = (fin - inicio).dt.total_seconds() / 3600
    salida["intervalo_negativo"] = horas.lt(0).fillna(False)
    salida["duracion_horas"] = horas.where(horas.ge(0)).round(3)
    salida["fecha_invalida_o_ausente"] = inicio.isna()
    salida["fuera_de_periodo"] = ~salida["anio_evento"].isin(list(anios_estudio))
    return salida


def exportar_csv(df, ruta):
    """Exporta en UTF-8 con BOM y fin de línea \\n (mismo archivo en cualquier sistema)."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8-sig", lineterminator="\n")
    return ruta


# ==========================================================
# 4. FLUJO COMPLETO
# ==========================================================

def consolidar(entrada, salida, docs, informar=print):
    """
    Ejecuta la consolidación completa y exporta los tres archivos.

    Devuelve un diccionario con las cifras del resumen.
    """
    tablas, inventario, meses = cargar_publicaciones(entrada, informar)
    publicaciones = consolidar_publicaciones(tablas)
    eventos, repetidos, sin_id = seleccionar_ultima_version(publicaciones)
    eventos = derivar_variables_temporales(eventos)

    exportar_csv(publicaciones, Path(salida) / "cen_fallas_2024_2026_publicaciones.csv")
    exportar_csv(eventos, Path(salida) / "cen_fallas_2024_2026_eventos.csv")
    exportar_csv(inventario, Path(docs) / "inventario_fallas_2024_2026.csv")

    return {
        "meses": meses,
        "publicados": len(publicaciones),
        "repetidos": repetidos,
        "sin_identificador": sin_id,
        "eventos": len(eventos),
        "duracion_valida": int(eventos["duracion_horas"].notna().sum()),
        "intervalo_negativo": int(eventos["intervalo_negativo"].sum()),
        "anio_evento": eventos["anio_evento"].value_counts(dropna=False).sort_index(),
    }


def imprimir_resumen(resumen):
    """Muestra el resumen de la consolidación en la terminal."""
    print("\n==========================================")
    print("RESUMEN DE CONSOLIDACIÓN HISTÓRICA")
    print("==========================================")
    meses = resumen["meses"]
    print("Meses procesados:", len(meses))
    for anio in ANIOS_ESTUDIO:
        presentes = sorted(m for a, m in meses if a == anio)
        print(f"\nAño {anio} - Meses encontrados:", presentes)
        # Para 2024 y 2025 se esperan años completos.
        if anio in (2024, 2025):
            pendientes = sorted(set(range(1, 13)) - set(presentes))
            if pendientes:
                print(f"AVISO: faltan meses de {anio}:", pendientes)
    print("\nRegistros publicados:", resumen["publicados"])
    print("Registros repetidos por identificador:", resumen["repetidos"])
    print("Registros sin identificador:", resumen["sin_identificador"])
    print("Eventos consolidados:", resumen["eventos"])
    print("Eventos con duración válida:", resumen["duracion_valida"])
    print("Eventos con intervalo negativo:", resumen["intervalo_negativo"])
    print("\nEVENTOS SEGÚN AÑO DE OCURRENCIA")
    print(resumen["anio_evento"])
    print("\nCONSOLIDACIÓN FINALIZADA CORRECTAMENTE")


def main(argumentos=None):
    parser = argparse.ArgumentParser(description="Consolida los informes de falla del CEN.")
    parser.add_argument("--entrada", default=RAIZ / "data" / "raw", type=Path,
                        help="carpeta con los ZIP (por defecto, data/raw)")
    parser.add_argument("--salida", default=RAIZ / "data" / "processed", type=Path,
                        help="carpeta de los CSV consolidados (por defecto, data/processed)")
    parser.add_argument("--docs", default=None, type=Path,
                        help="carpeta del inventario (por defecto, docs/ o --salida si se indica)")
    args = parser.parse_args(argumentos)
    # Si se cambia la salida (por ejemplo, para una prueba), el inventario va
    # junto a ella y no sobrescribe docs/.
    salida_por_defecto = Path(args.salida).resolve() == (RAIZ / "data" / "processed").resolve()
    docs = args.docs or (RAIZ / "docs" if salida_por_defecto else args.salida)
    try:
        resumen = consolidar(args.entrada, args.salida, docs)
    except ErrorConsolidacion as error:
        raise SystemExit(str(error)) from error
    imprimir_resumen(resumen)
    return resumen


if __name__ == "__main__":
    main()
