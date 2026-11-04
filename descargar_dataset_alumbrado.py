"""MCDI500 — descarga reproducible de incidencias de alumbrado público (NYC 311).

Origen oficial: NYC Open Data, 311 Service Requests from 2020 to Present.
Dataset id: erm2-nwe9
Años incluidos: 2025 y 2026 (hasta octubre, inclusive).

Ejecución desde la raíz del proyecto en Visual Studio Code:
    python descargar_dataset_alumbrado.py

Luego:
    python validar_dataset.py data/raw/incidencias_alumbrado_2025_2026.csv --informe docs/validacion_dataset.md

Requiere pandas y acceso a Internet. No genera datos ficticios ni añade valores faltantes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import hashlib
import subprocess
import sys

import pandas as pd


ORIGEN = "https://data.cityofnewyork.us/resource/erm2-nwe9.csv"
FICHA = "https://data.cityofnewyork.us/d/erm2-nwe9"
CONDICION = "Street Light Condition"
REGISTROS_POR_PERIODO = 5000
PERIODOS = (
    ("2025-01-01T00:00:00", "2026-01-01T00:00:00"),
    ("2026-01-01T00:00:00", "2026-11-01T00:00:00"),
)

# Se excluyen dirección postal del solicitante, teléfono, nombres y observaciones
# aportadas directamente por usuarios. Los campos corresponden a incidencias públicas.
CAMPOS = (
    "unique_key",
    "created_date",
    "closed_date",
    "resolution_action_updated_date",
    "agency",
    "agency_name",
    "complaint_type",
    "descriptor",
    "status",
    "resolution_description",
    "borough",
    "community_board",
    "city",
    "incident_zip",
    "latitude",
    "longitude",
    "open_data_channel_type",
    "council_district",
    "police_precinct",
    "location_type",
)

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "data" / "raw" / "incidencias_alumbrado_2025_2026.csv"
DOCUMENTACION = RAIZ / "docs" / "fuente_dataset.md"
INFORME = RAIZ / "docs" / "validacion_dataset.md"


def obtener_periodo(desde: str, hasta: str) -> tuple[pd.DataFrame, str]:
    filtro = (
        f"complaint_type = '{CONDICION}' "
        f"AND created_date >= '{desde}' AND created_date < '{hasta}'"
    )
    parametros = {
        "$select": ",".join(CAMPOS),
        "$where": filtro,
        "$order": "created_date DESC,unique_key DESC",
        "$limit": REGISTROS_POR_PERIODO,
    }
    url = f"{ORIGEN}?{urlencode(parametros)}"
    solicitud = Request(
        url,
        headers={
            "User-Agent": "ProyectoAcademico-MCDI500/1.0",
            "Accept": "text/csv",
        },
    )
    try:
        with urlopen(solicitud, timeout=120) as respuesta:
            contenido = respuesta.read()
    except HTTPError as exc:
        detalle = exc.read(700).decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Error HTTP {exc.code} al consultar NYC Open Data: {detalle}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"No se pudo conectar con la fuente oficial: {exc}") from exc

    try:
        datos = pd.read_csv(BytesIO(contenido), encoding="utf-8-sig", low_memory=False)
    except Exception as exc:
        raise RuntimeError(f"La descarga no pudo interpretarse como CSV: {exc}") from exc

    if datos.empty:
        raise RuntimeError(f"El servidor devolvió cero registros para {desde} a {hasta}.")
    return datos, url


def main() -> int:
    print("DESCARGA DEL DATASET OFICIAL — MCDI500")
    print("Fuente: NYC Open Data / NYC 311 / Street Light Condition")
    partes = []
    consultas = []
    for inicio, fin in PERIODOS:
        print(f"Consultando periodo {inicio[:10]} a {fin[:10]} ...", flush=True)
        datos, url = obtener_periodo(inicio, fin)
        print(f"  Registros recibidos: {len(datos):,}")
        partes.append(datos)
        consultas.append(url)

    df = pd.concat(partes, ignore_index=True)
    if "unique_key" not in df.columns:
        raise RuntimeError("La API no entregó la clave única de los registros.")
    duplicados = int(df["unique_key"].duplicated().sum())
    if duplicados:
        raise RuntimeError(
            f"Se encontraron {duplicados} identificadores duplicados. "
            "Revisar la extracción; no se alterarán silenciosamente los datos."
        )

    # Se omiten de la extracción final únicamente campos casi vacíos (>60 % NA).
    # Los valores faltantes de los demás campos se conservan SIN imputar.
    proporcion_faltante = df.isna().mean()
    omitidas = [c for c in df.columns if proporcion_faltante[c] > 0.60]
    if omitidas:
        print("Columnas omitidas por tener más de 60% de valores faltantes:")
        print("  " + ", ".join(omitidas))
        df = df.drop(columns=omitidas)

    if len(df) < 2000 or len(df.columns) < 12:
        raise RuntimeError(
            f"El extracto solo tiene {len(df)} filas y {len(df.columns)} columnas. "
            "No alcanza el mínimo; no se guardará un archivo que parezca elegible."
        )
    if df.empty:
        raise RuntimeError("No hay registros para guardar.")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    DOCUMENTACION.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA, index=False, encoding="utf-8")

    sha256 = hashlib.sha256(SALIDA.read_bytes()).hexdigest()
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    texto_consultas = "\n".join(f"- {url}" for url in consultas)
    DOCUMENTACION.write_text(
        f"# Procedencia y delimitación del dataset — MCDI500\n\n"
        f"**Fuente:** NYC 311 / NYC Open Data (organismo público municipal).\n\n"
        f"**Ficha oficial:** {FICHA}\n\n"
        f"**Condición:** `complaint_type = '{CONDICION}'`.\n\n"
        f"**Intervalo:** del 01-01-2025 al 31-10-2026.\n\n"
        f"**Extracción:** hasta {REGISTROS_POR_PERIODO} registros por periodo (2025 y 2026), "
        f"ordenados por fecha descendente. No es una muestra probabilística: "
        f"las inferencias se limitan a esta selección de casos.\n\n"
        f"**Descargado el:** {fecha}.\n\n"
        f"**Archivo:** `{SALIDA.relative_to(RAIZ)}`.\n\n"
        f"**Dimensiones:** {df.shape[0]:,} filas × {df.shape[1]} columnas.\n\n"
        f"**SHA-256:** `{sha256}`.\n\n"
        f"**Campos omitidos al preparar el extracto por >60% NA:** "
        f"{', '.join(omitidas) if omitidas else 'ninguno'}.\n\n"
        f"**Tratamiento de datos:** no se crean registros ni se imputan valores; "
        f"los campos conservados se mantienen como fueron publicados. "
        f"La limpieza analítica se realizará por separado en Fase 2.\n\n"
        f"**Privacidad:** no se solicitan nombres, correos, teléfonos ni "
        f"direcciones postales de quienes contactaron al servicio 311. "
        f"Antes de compartirlo públicamente, revisar el contenido textual de resolución.\n\n"
        f"**Condiciones de uso:** verificar y citar los Términos de Uso del portal "
        f"NYC Open Data y la ficha de origen.\n\n"
        f"**Advertencia metodológica:** esta base refleja solicitudes de servicio, "
        f"no fallas confirmadas de activos ni tiempos de reparación reales. "
        f"El cierre administrativo de una solicitud no siempre equivale a una reparación.\n\n"
        f"## Consultas reproducibles\n\n{texto_consultas}\n",
        encoding="utf-8",
    )

    print(f"\nArchivo guardado: {SALIDA}")
    print(f"Dimensiones: {len(df):,} filas y {len(df.columns)} columnas")
    print(f"Valores faltantes totales: {int(df.isna().sum().sum()):,}")
    print(f"Tamaño: {SALIDA.stat().st_size / (1024 * 1024):.2f} MB")
    print(f"Documentación: {DOCUMENTACION}")
    print("\nEjecutando el validador del profesor ...")
    validador = RAIZ / "validar_dataset.py"
    if validador.exists():
        proc = subprocess.run(
            [sys.executable, str(validador), str(SALIDA), "--informe", str(INFORME)],
            check=False,
        )
        if proc.returncode == 0:
            print("\nCONFIRMADO: cumple los cinco requisitos obligatorios del validador.")
        else:
            print("\nATENCION: revisar los avisos o requisitos del validador.")
        return proc.returncode
    print("El archivo validar_dataset.py no está en la raíz. Ejecútalo manualmente.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError) as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
