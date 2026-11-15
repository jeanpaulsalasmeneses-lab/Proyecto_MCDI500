"""
Operaciones territoriales sin estado (Fase 3).

Reproducen las reglas de F2 (§5 y §6.5) como funciones reutilizables:

- limpiar_texto / normalizar_comuna   claves de comparación sin tildes ni mayúsculas
- separar_vinculos_bucle              versión de F2: recorre informe por informe
- separar_vinculos_vectorizado        misma salida, con operaciones de pandas
- cargar_maestro_ine                  346 comunas oficiales del Censo 2024
- cargar_equivalencias                data/reference/equivalencias_comunas.csv

Son funciones, no clases, porque no aprenden nada de los datos: dado el
mismo valor de entrada, siempre devuelven lo mismo (guía de la Sumativa 2,
paso 2). Lo que sí aprende (el maestro de comunas y la población) está en
src/transformadores.py.
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd

COLUMNAS_VINCULOS = ["id_falla", "comuna_reportada", "comuna_clave", "zona_afectada"]


def limpiar_texto(valor):
    """Reduce los espacios repetidos y recorta los extremos. Vacío o NA -> NA."""
    if pd.isna(valor):
        return pd.NA
    texto = re.sub(r"\s+", " ", str(valor)).strip()
    return texto if texto else pd.NA


def normalizar_comuna(valor):
    """
    Clave de comparación: sin tildes, en mayúsculas y sin espacios extra.

    >>> normalizar_comuna("  Viña   del Mar ")
    'VINA DEL MAR'
    """
    texto = limpiar_texto(valor)
    if pd.isna(texto):
        return pd.NA
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.upper()


def separar_vinculos_bucle(eventos):
    """
    Versión de F2 (§5): recorre informe por informe y comuna por comuna.

    Cada informe con varias comunas («A | B») genera un vínculo por comuna.
    Se descartan los vínculos repetidos del mismo informe.
    """
    vinculos = []
    for id_falla, comunas, zona in eventos[["id_falla", "Comuna", "Zona Afectada"]].itertuples(
            index=False, name=None):
        comunas = limpiar_texto(comunas)
        if pd.isna(comunas):
            continue
        zona = limpiar_texto(zona)
        for comuna in str(comunas).split("|"):
            comuna = limpiar_texto(comuna)
            if pd.isna(comuna):
                continue
            vinculos.append({"id_falla": id_falla, "comuna_reportada": comuna,
                             "comuna_clave": normalizar_comuna(comuna), "zona_afectada": zona})
    tabla = pd.DataFrame(vinculos, columns=COLUMNAS_VINCULOS)
    return tabla.drop_duplicates(subset=["id_falla", "comuna_clave"]).reset_index(drop=True)


def separar_vinculos_vectorizado(eventos):
    """
    Misma salida que separar_vinculos_bucle, sin recorrer fila por fila:

    1. split + explode de pandas separan todas las listas de una vez;
    2. la clave se calcula una sola vez por nombre distinto (320 nombres en
       lugar de 23.284 vínculos) y se asigna con map.
    """
    base = eventos[["id_falla", "Comuna", "Zona Afectada"]].copy()
    base["Comuna"] = base["Comuna"].map(limpiar_texto)
    base = base.loc[base["Comuna"].notna()]
    zona = base["Zona Afectada"].map(limpiar_texto)

    separadas = base.assign(zona_afectada=zona)["Comuna"].astype(str).str.split("|").explode()
    tabla = pd.DataFrame({
        "id_falla": base.loc[separadas.index, "id_falla"].to_numpy(),
        "comuna_reportada": separadas.map(limpiar_texto).to_numpy(),
        "zona_afectada": zona.loc[separadas.index].to_numpy(),
    })
    tabla = tabla.loc[tabla["comuna_reportada"].notna()]
    nombres = tabla["comuna_reportada"].unique()
    claves = {nombre: normalizar_comuna(nombre) for nombre in nombres}
    tabla["comuna_clave"] = tabla["comuna_reportada"].map(claves)
    tabla = tabla[COLUMNAS_VINCULOS]
    return tabla.drop_duplicates(subset=["id_falla", "comuna_clave"]).reset_index(drop=True)


def cargar_maestro_ine(ruta_excel):
    """
    Maestro de comunas oficiales del Censo 2024 (F2 §6.5).

    Hoja «2» del Excel del INE: se conservan las filas comunales (código > 0)
    con código de 5 dígitos, nombre oficial, clave normalizada, región y
    población.
    """
    ine = pd.read_excel(ruta_excel, sheet_name="2", header=3)
    ine.columns = ine.columns.astype(str).str.strip()
    faltan = {"Código comuna", "Comuna", "Región", "Población censada"} - set(ine.columns)
    if faltan:
        raise ValueError(f"Faltan columnas del INE: {sorted(faltan)}")

    codigos = pd.to_numeric(ine["Código comuna"], errors="coerce")
    ine = ine.loc[codigos.gt(0)].copy()
    maestro = pd.DataFrame({
        "codigo_comuna": pd.to_numeric(ine["Código comuna"]).astype("Int64").astype("string").str.zfill(5),
        "comuna_oficial": ine["Comuna"].astype("string").str.strip(),
        "region_oficial": ine["Región"].astype("string").str.strip(),
        "poblacion_2024": pd.to_numeric(ine["Población censada"], errors="coerce"),
    })
    maestro["comuna_clave"] = maestro["comuna_oficial"].map(normalizar_comuna).astype("string")
    return maestro.reset_index(drop=True)


def cargar_equivalencias(ruta_csv):
    """Tabla clave_cen -> clave_ine de data/reference/ (decisión D-02)."""
    return pd.read_csv(Path(ruta_csv), dtype=str, encoding="utf-8")
