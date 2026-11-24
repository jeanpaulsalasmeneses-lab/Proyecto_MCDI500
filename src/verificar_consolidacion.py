"""
Verifica que el script de consolidación reproduce los archivos versionados.

Responde al punto 5 de la retroalimentación de F3: «Versionen el código que
compara el script de consolidación con los archivos consolidados, para que
esa equivalencia también se pueda reproducir.» Hasta ahora, esa comparación
se había hecho a mano.

Flujo:

    data/raw/ (33 ZIP del CEN)
      -> consolidar()           en una carpeta temporal, sin tocar data/processed/
      -> comparar_archivos()    SHA-256 de cada archivo nuevo frente al versionado
      -> informe                COINCIDE / FIN_DE_LINEA / DIFIERE / FALTA

FIN_DE_LINEA significa que los archivos son idénticos salvo el fin de línea
(\r\n frente a \n). Es lo esperado para los dos consolidados de
data/processed/: se versionaron el 2026-11-05 desde Windows, con \r\n, y el
script escribe \n desde la decisión D-04. El contenido es el mismo, celda por
celda (ver docs/fuente_dataset.md).

Uso, desde la raíz del proyecto (requiere los ZIP en data/raw/; si no están,
se descargan con python src/descargar_cen.py):

    python src/verificar_consolidacion.py

Termina con código 0 si cada archivo coincide byte a byte o solo difiere en
el fin de línea, 1 si alguno difiere en contenido y 2 si faltan los ZIP. Las funciones de comparación se prueban en
tests/test_verificar_consolidacion.py, sin necesidad de los ZIP.
"""

import hashlib
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.consolidar_fallas_2024_2026 import consolidar  # noqa: E402

# Archivo generado por consolidar() -> archivo versionado con el que se compara.
ARCHIVOS = {
    "cen_fallas_2024_2026_publicaciones.csv":
        RAIZ / "data" / "processed" / "cen_fallas_2024_2026_publicaciones.csv",
    "cen_fallas_2024_2026_eventos.csv":
        RAIZ / "data" / "processed" / "cen_fallas_2024_2026_eventos.csv",
    "inventario_fallas_2024_2026.csv":
        RAIZ / "docs" / "inventario_fallas_2024_2026.csv",
}


def sha256(ruta, bloque=1024 * 1024):
    """Huella SHA-256 de un archivo, leído por bloques."""

    calculador = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for parte in iter(lambda: archivo.read(bloque), b""):
            calculador.update(parte)
    return calculador.hexdigest()


def iguales_salvo_fin_de_linea(ruta_a, ruta_b):
    """True si los archivos son idénticos al llevar todo \r\n a \n."""

    def normalizado(ruta):
        return Path(ruta).read_bytes().replace(b"\r\n", b"\n")

    return normalizado(ruta_a) == normalizado(ruta_b)


def comparar_archivos(versionado, generado):
    """
    Compara dos archivos por su SHA-256.

    Devuelve un diccionario con el estado y las dos huellas, para que el
    resultado quede registrado y no solo impreso:
    COINCIDE (byte a byte), FIN_DE_LINEA (idénticos salvo \r\n frente a \n,
    decisión D-04), DIFIERE o FALTA.
    """

    versionado, generado = Path(versionado), Path(generado)
    faltantes = [str(r) for r in (versionado, generado) if not r.is_file()]
    if faltantes:
        return {"estado": "FALTA", "faltantes": faltantes,
                "sha_versionado": None, "sha_generado": None}

    huella_v, huella_g = sha256(versionado), sha256(generado)
    if huella_v == huella_g:
        estado = "COINCIDE"
    elif iguales_salvo_fin_de_linea(versionado, generado):
        estado = "FIN_DE_LINEA"
    else:
        estado = "DIFIERE"
    return {"estado": estado,
            "faltantes": [], "sha_versionado": huella_v, "sha_generado": huella_g}


def comparar_carpeta(carpeta_generada, archivos=ARCHIVOS):
    """Compara cada archivo generado con su versión en el repositorio."""

    return {nombre: comparar_archivos(versionado, Path(carpeta_generada) / nombre)
            for nombre, versionado in archivos.items()}


def verificar(entrada=RAIZ / "data" / "raw"):
    """
    Reconstruye los consolidados en una carpeta temporal y los compara.

    Devuelve (resultados, resumen_de_consolidar). No escribe en data/processed/
    ni en docs/.
    """

    with tempfile.TemporaryDirectory() as temporal:
        resumen = consolidar(entrada, temporal, temporal, informar=lambda *_: None)
        resultados = comparar_carpeta(temporal)
    return resultados, resumen


def main():
    entrada = RAIZ / "data" / "raw"
    zips = sorted(entrada.glob("*.zip"))
    if not zips:
        print("No hay ZIP en data/raw/. Descárguelos con: python src/descargar_cen.py")
        return 2

    print(f"Reconstruyendo los consolidados desde {len(zips)} ZIP en una carpeta temporal…")
    resultados, resumen = verificar(entrada)
    print(f"Registros publicados: {resumen['publicados']:,} · "
          f"eventos consolidados: {resumen['eventos']:,}\n")

    for nombre, r in resultados.items():
        if r["estado"] == "COINCIDE":
            detalle = f"idéntico byte a byte ({r['sha_generado'][:16]}…)"
        elif r["estado"] == "FIN_DE_LINEA":
            detalle = "idéntico salvo el fin de línea (versionado \\r\\n, script \\n; D-04)"
        elif r["estado"] == "DIFIERE":
            detalle = (f"versionado {r['sha_versionado'][:12]} ≠ "
                       f"generado {r['sha_generado'][:12]}")
        else:
            detalle = f"falta {r['faltantes']}"
        print(f"[{r['estado']}] {nombre}: {detalle}")

    reproduce = all(r["estado"] in ("COINCIDE", "FIN_DE_LINEA")
                    for r in resultados.values())
    print("\n[OK] El script reproduce el contenido de los archivos versionados."
          if reproduce else
          "\n[ERROR] El script no reproduce los archivos versionados.")
    return 0 if reproduce else 1


if __name__ == "__main__":
    raise SystemExit(main())
