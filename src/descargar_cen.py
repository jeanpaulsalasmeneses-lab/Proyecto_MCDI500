# ==========================================================
# MAGÍSTER EN CIENCIA DE DATOS E INTELIGENCIA ARTIFICIAL
# ASIGNATURA: MCDI500
# GRUPO 7
#
# DESCARGA DE LOS DATOS ORIGINALES DEL CEN
# "Desconexiones e intervenciones / informes de falla / limitaciones"
# PERÍODO: enero 2024 - septiembre 2026 (33 publicaciones mensuales)
#
# Uso, desde la raíz del proyecto y con el entorno activo:
#     python src/descargar_cen.py
#
# Deja los ZIP en data/raw/ (no se versionan) y escribe
# docs/descargas_cen.csv (sí se versiona) con la URL, el tamaño,
# el SHA-256 y la fecha de publicación de cada archivo. Ese registro
# indica exactamente qué versión de los datos usó el proyecto.
# ==========================================================

import csv
import hashlib
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zipfile import BadZipFile, ZipFile


# ==========================================================
# 1. CONFIGURACIÓN
# ==========================================================

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "data" / "raw"
REGISTRO = RAIZ / "docs" / "descargas_cen.csv"

# Página donde el CEN publica los archivos (para citarla):
# https://www.coordinador.cl/operacion/graficos/desconexiones-e-intervenciones/
# Cada enlace "Descargar" de esa página sigue este patrón:
URL = (
    "https://cen-datalake-public.s3.amazonaws.com/conexiones_intervenciones/"
    "{anio}/{mes:02d}/{anio}_{mes:02d}_conexiones_intervenciones.zip"
)

PERIODOS = (
    [(2024, m) for m in range(1, 13)]
    + [(2025, m) for m in range(1, 13)]
    + [(2026, m) for m in range(1, 10)]
)

AGENTE = "Proyecto-MCDI500-Grupo7/1.0 (uso academico)"


# ==========================================================
# 2. FUNCIONES
# ==========================================================

def sha256(ruta):
    """Huella SHA-256 de un archivo."""
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def zip_valido(ruta):
    """True si el archivo es un ZIP legible y trae el informe de fallas."""
    try:
        with ZipFile(ruta) as z:
            return z.testzip() is None and any(
                n.endswith("_informe_fallas.csv") for n in z.namelist()
            )
    except BadZipFile:
        return False


def descargar(url, ruta, intentos=3):
    """Descarga url en ruta (vía archivo temporal). Devuelve Last-Modified."""
    temporal = ruta.with_suffix(".parcial")
    for intento in range(1, intentos + 1):
        try:
            pedido = urllib.request.Request(url, headers={"User-Agent": AGENTE})
            with urllib.request.urlopen(pedido, timeout=60) as r, open(temporal, "wb") as f:
                publicado = r.headers.get("Last-Modified", "")
                while bloque := r.read(1 << 20):
                    f.write(bloque)
            temporal.replace(ruta)
            return publicado
        except OSError as error:
            print(f"   intento {intento}/{intentos} falló: {error}")
            time.sleep(2 * intento)
    temporal.unlink(missing_ok=True)
    raise SystemExit(f"No se pudo descargar {url}")


# ==========================================================
# 3. DESCARGA
# ==========================================================

def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    forzar = "--forzar" in sys.argv
    filas = []

    for anio, mes in PERIODOS:
        url = URL.format(anio=anio, mes=mes)
        ruta = DESTINO / Path(url).name

        if ruta.exists() and zip_valido(ruta) and not forzar:
            publicado = ""
            estado = "ya existía"
        else:
            publicado = descargar(url, ruta)
            if not zip_valido(ruta):
                raise SystemExit(f"ZIP dañado o sin informe de fallas: {ruta.name}")
            estado = "descargado"

        filas.append({
            "anio": anio,
            "mes": mes,
            "archivo": ruta.name,
            "url": url,
            "bytes": ruta.stat().st_size,
            "sha256": sha256(ruta),
            "publicado_cen": publicado,
            "fecha_descarga": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
        print(f"OK {anio}-{mes:02d}: {estado} ({filas[-1]['bytes']:,} bytes)")

    with open(REGISTRO, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"\n{len(filas)} archivos en {DESTINO.relative_to(RAIZ)}")
    print(f"Registro: {REGISTRO.relative_to(RAIZ)}")
    print("Siguiente paso: python src/consolidar_fallas_2024_2026.py")


if __name__ == "__main__":
    main()
