"""
Verificación del entorno y trazabilidad de ejecución — Proyecto MCDI500 · Grupo 7.

Lo usan F1 y F2 al inicio para dejar constancia, en la salida del notebook, de:

1. Qué intérprete y qué entorno virtual se usaron.
2. Que cada dependencia de requirements.txt está instalada con la versión
   declarada (verificación componente por componente, no supuesta).
3. En qué commit y rama de Git se produjeron los resultados.
4. La semilla aleatoria. El pipeline no usa procesos aleatorios, pero la semilla
   se fija igual, para que un muestreo futuro sea reproducible.

Uso desde un notebook:

    import sys
    from pathlib import Path
    RAIZ = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "src" / "trazabilidad.py").is_file())
    sys.path.insert(0, str(RAIZ / "src"))
    from trazabilidad import informe_entorno
    informe_entorno(RAIZ)
"""

import platform
import random
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2024


def fijar_semilla(semilla=SEMILLA):
    """Fija la semilla de random y de NumPy. Devuelve la semilla usada."""
    random.seed(semilla)
    np.random.seed(semilla)
    return semilla


def dependencias_declaradas(ruta_requirements):
    """
    Lee requirements.txt y devuelve {paquete: versión} de las líneas que aplican
    a este sistema operativo (respeta marcadores como sys_platform == "win32").
    """
    try:
        from packaging.markers import Marker
    except ImportError:          # packaging viene con pip/jupyter; por si acaso
        Marker = None

    declaradas = {}
    for linea in Path(ruta_requirements).read_text(encoding="utf-8").splitlines():
        linea = linea.split("#", 1)[0].strip()
        if not linea or "==" not in linea:
            continue
        requisito, _, marcador = linea.partition(";")
        if marcador.strip() and Marker is not None and not Marker(marcador.strip()).evaluate():
            continue
        nombre, _, version_fija = requisito.partition("==")
        declaradas[nombre.strip()] = version_fija.strip()
    return declaradas


def verificar_dependencias(ruta_requirements):
    """
    Compara cada dependencia declarada con la instalada.
    Devuelve un DataFrame con: paquete, declarada, instalada, coincide.
    """
    filas = []
    for nombre, declarada in dependencias_declaradas(ruta_requirements).items():
        try:
            instalada = version(nombre)
        except PackageNotFoundError:
            instalada = "NO INSTALADA"
        filas.append({
            "paquete": nombre,
            "declarada": declarada,
            "instalada": instalada,
            "coincide": instalada == declarada,
        })
    return pd.DataFrame(filas)


def estado_git(raiz):
    """Commit, rama y si hay cambios sin commit. Si Git no está, lo informa."""
    def git(*args):
        try:
            return subprocess.run(
                ["git", *args], cwd=raiz, capture_output=True, text=True, check=True
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    commit = git("rev-parse", "--short", "HEAD")
    if commit is None:
        return {"commit": "no disponible (sin Git)", "rama": "-", "cambios_sin_commit": "-"}
    return {
        "commit": commit,
        "rama": git("rev-parse", "--abbrev-ref", "HEAD"),
        "cambios_sin_commit": "sí" if git("status", "--porcelain", "--untracked-files=no") else "no",
    }


def informe_entorno(raiz, paquetes_clave=("pandas", "numpy", "matplotlib", "openpyxl")):
    """
    Imprime la verificación del entorno y la trazabilidad, y falla con
    AssertionError si no hay entorno virtual o si alguna versión no coincide.
    Devuelve el DataFrame de dependencias para inspeccionarlo.
    """
    raiz = Path(raiz)
    semilla = fijar_semilla()
    git = estado_git(raiz)
    deps = verificar_dependencias(raiz / "requirements.txt")

    print("=" * 65)
    print("VERIFICACIÓN DEL ENTORNO Y TRAZABILIDAD DE LA EJECUCIÓN")
    print("=" * 65)
    print(f"Python {platform.python_version()} · {platform.system()} {platform.release()}")
    print(f"Entorno virtual activo: {'sí' if sys.prefix != sys.base_prefix else 'NO'}")
    print(f"Raíz del proyecto: {raiz.name}/ (rutas relativas a esta carpeta)")
    print(f"Commit: {git['commit']} · rama: {git['rama']} · cambios sin commit: {git['cambios_sin_commit']}")
    print(f"Semilla aleatoria: {semilla} (el pipeline no usa procesos aleatorios)")
    print(f"\nDependencias de requirements.txt verificadas: "
          f"{int(deps['coincide'].sum())} de {len(deps)} coinciden con la versión declarada")
    print(deps.loc[deps["paquete"].isin(paquetes_clave)].to_string(index=False))

    assert sys.prefix != sys.base_prefix, "El kernel no usa un entorno virtual (.venv)."
    distintas = deps.loc[~deps["coincide"]]
    assert distintas.empty, f"Versiones distintas a requirements.txt:\n{distintas.to_string(index=False)}"
    print("\n[OK] Entorno verificado componente por componente.")
    return deps
