"""
Normalización de las descripciones causales del CEN (F4).

Responde al punto 3 de la retroalimentación de F3: las descripciones con
errores de escritura se corrigen con una tabla de equivalencias versionada,
igual que las comunas (D-02), y no solo en la leyenda de una figura.

- La tabla vive en data/reference/equivalencias_causas.csv, escrita a mano.
- Solo corrige errores de escritura. No agrupa causas distintas: unir
  categorías del CEN sería una decisión analítica, no una corrección.
- Se aplica en la capa de comunicación (F4), sobre una copia. Los
  artefactos de F2 y F3 conservan el texto tal como lo publica el CEN, para
  que sigan siendo trazables a la fuente y no cambien sus SHA-256 (D-15).
"""

from pathlib import Path

import pandas as pd

from src.indicadores import verificar_columnas

RUTA_EQUIVALENCIAS = (
    Path(__file__).resolve().parent.parent
    / "data" / "reference" / "equivalencias_causas.csv"
)

COLUMNAS = ["descripcion_cen", "descripcion_normalizada", "motivo"]


def cargar_equivalencias_causas(ruta_csv=RUTA_EQUIVALENCIAS):
    """
    Lee la tabla de equivalencias y comprueba que sea utilizable.

    Falla si faltan columnas, si una descripción del CEN aparece dos veces
    (la corrección sería ambigua) o si una corrección es a su vez una
    descripción a corregir (cadena de equivalencias).
    """

    tabla = pd.read_csv(Path(ruta_csv), dtype=str, encoding="utf-8")
    verificar_columnas(tabla, COLUMNAS, "equivalencias_causas")

    if tabla[COLUMNAS].isna().any().any():
        raise ValueError("equivalencias_causas tiene celdas vacías.")

    repetidas = tabla.loc[tabla["descripcion_cen"].duplicated(),
                          "descripcion_cen"].tolist()
    if repetidas:
        raise ValueError(
            f"equivalencias_causas repite descripciones del CEN: {repetidas}"
        )

    encadenadas = sorted(
        set(tabla["descripcion_normalizada"]) & set(tabla["descripcion_cen"])
    )
    if encadenadas:
        raise ValueError(
            "Una corrección es a su vez una descripción a corregir: "
            f"{encadenadas}"
        )

    return tabla


def normalizar_descripcion_causa(serie, equivalencias):
    """
    Devuelve una copia de la serie con las descripciones corregidas.

    Las descripciones que no están en la tabla y los valores faltantes
    quedan iguales. La serie original no se modifica.
    """

    verificar_columnas(equivalencias, COLUMNAS[:2], "equivalencias")
    mapa = dict(zip(equivalencias["descripcion_cen"],
                    equivalencias["descripcion_normalizada"]))

    return serie.map(lambda valor: mapa.get(valor, valor))
