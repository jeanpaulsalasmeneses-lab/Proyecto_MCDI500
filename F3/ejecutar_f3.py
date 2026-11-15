# ==========================================================
# FASE 3 - EJECUCIÓN INDEPENDIENTE DEL SISTEMA
# PROYECTO MCDI500 - GRUPO 7
# ==========================================================

from pathlib import Path
import hashlib
import json
import sys

import pandas as pd

# El núcleo vive en src/: se importa desde la raíz del proyecto.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.nucleo import NucleoAnalitico

from src.indicadores import construir_panel_integrado

from src.recorridos import (
    construir_jerarquia,
    sumar_asociaciones_recursivo,
    sumar_asociaciones_iterativo
)


# ==========================================================
# 1. IDENTIFICAR DIRECTORIOS
# ==========================================================

CARPETA_F3 = Path(__file__).resolve().parent

RAIZ = CARPETA_F3.parent

CARPETA_DATOS = RAIZ / "data" / "processed" / "f2"

CARPETA_RESULTADOS = CARPETA_F3 / "resultados"

CARPETA_RESULTADOS.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# 2. IDENTIFICAR ARCHIVOS DE ENTRADA
# ==========================================================

archivos = {
    "informes": "03_cen_informes_prioritarios.csv",
    "asociaciones": "04_cen_fallas_comunas_integrado.csv",
    "comunas": "05_cen_perfiles_15_comunas.csv"
}

for nombre in archivos.values():

    ruta = CARPETA_DATOS / nombre

    if not ruta.is_file():

        raise FileNotFoundError(
            f"Archivo de F2 no disponible: {ruta}"
        )


# ==========================================================
# 3. CALCULAR HUELLAS SHA-256
# ==========================================================

def calcular_sha256(ruta):
    """
    Calcula la huella SHA-256 de un archivo
    utilizando lectura por bloques.
    """

    digest = hashlib.sha256()

    with open(ruta, "rb") as archivo:

        for bloque in iter(
            lambda: archivo.read(1024 * 1024),
            b""
        ):

            digest.update(bloque)

    return digest.hexdigest()


# ==========================================================
# 4. AUDITAR INTEGRIDAD DE ARCHIVOS F2
# ==========================================================

ruta_manifiesto = CARPETA_DATOS / "manifest_f2.json"

auditoria_sha = []

if ruta_manifiesto.is_file():

    manifiesto = json.loads(
        ruta_manifiesto.read_text(
            encoding="utf-8"
        )
    )

    registros = {
        registro["archivo"]: registro
        for registro in manifiesto["archivos"]
    }

    for nombre in archivos.values():

        ruta = CARPETA_DATOS / nombre

        sha_actual = calcular_sha256(ruta)

        if nombre in registros:

            sha_esperado = registros[nombre].get(
                "sha256"
            )

        else:

            sha_esperado = None

        if sha_esperado is None:

            estado = "SIN_REFERENCIA"

        elif sha_actual == sha_esperado:

            estado = "COINCIDE"

        else:

            estado = "DIFIERE"

        auditoria_sha.append({
            "archivo": nombre,
            "sha256_manifiesto": sha_esperado,
            "sha256_actual": sha_actual,
            "estado": estado
        })

        print(
            f"[SHA-256] {nombre}: {estado}"
        )

else:

    print(
        "[ADVERTENCIA] No se encontró manifest_f2.json."
    )

    for nombre in archivos.values():

        ruta = CARPETA_DATOS / nombre

        auditoria_sha.append({
            "archivo": nombre,
            "sha256_manifiesto": None,
            "sha256_actual": calcular_sha256(ruta),
            "estado": "SIN_MANIFIESTO"
        })


# ==========================================================
# 5. EXPORTAR AUDITORÍA SHA-256
# ==========================================================

ruta_auditoria = (
    CARPETA_RESULTADOS
    / "F3_803_Auditoria_SHA256.json"
)

ruta_auditoria.write_text(
    json.dumps(
        auditoria_sha,
        ensure_ascii=False,
        indent=4
    ),
    encoding="utf-8"
)

estados_sha = {
    registro["estado"]
    for registro in auditoria_sha
}

integridad_binaria_confirmada = (
    estados_sha == {"COINCIDE"}
)

if integridad_binaria_confirmada:

    print(
        "[OK] Integridad binaria respecto "
        "del manifiesto F2 confirmada."
    )

else:

    print(
        "[ADVERTENCIA] La integridad binaria "
        "de F2 presenta diferencias o "
        "referencias no verificables."
    )

    print(
        "[INFO] Se continuará con la validación "
        "independiente de los datos y resultados."
    )

    print(
        "[INFO] La discrepancia queda registrada "
        "para su revisión posterior."
    )


# ==========================================================
# 6. FUNCIÓN DE CARGA DE ARCHIVOS CSV
# ==========================================================

def cargar_csv(nombre):
    """
    Carga un conjunto procesado de F2.
    Conserva identificadores como texto.
    """

    ruta = CARPETA_DATOS / nombre

    encabezado = pd.read_csv(
        ruta,
        encoding="utf-8-sig",
        nrows=0
    )

    tipos = {
        columna: "string"
        for columna in [
            "id_falla",
            "codigo_comuna"
        ]
        if columna in encabezado.columns
    }

    return pd.read_csv(
        ruta,
        encoding="utf-8-sig",
        dtype=tipos,
        low_memory=False
    )


# ==========================================================
# 7. CARGAR CONJUNTOS PROCESADOS DE F2
# ==========================================================

informes = cargar_csv(
    archivos["informes"]
)

asociaciones = cargar_csv(
    archivos["asociaciones"]
)

comunas = cargar_csv(
    archivos["comunas"]
)


# ==========================================================
# 8. VALIDAR DIMENSIONES DOCUMENTALES
# ==========================================================

assert len(informes) == 1834, (
    "Cantidad de informes inconsistente."
)

assert len(asociaciones) == 1915, (
    "Cantidad de asociaciones inconsistente."
)

assert len(comunas) == 15, (
    "Cantidad de comunas inconsistente."
)

assert informes["id_falla"].is_unique

assert comunas["codigo_comuna"].is_unique

assert not asociaciones.duplicated(
    ["id_falla", "codigo_comuna"]
).any()

assert (
    set(asociaciones["id_falla"])
    == set(informes["id_falla"])
)

assert (
    set(asociaciones["codigo_comuna"])
    == set(comunas["codigo_comuna"])
)

print("[OK] Integridad documental verificada.")

print(
    "[OK] 1.834 informes, 1.915 asociaciones "
    "y 15 comunas."
)


# ==========================================================
# 9. VERIFICAR VARIABLES TEMPORALES
# ==========================================================

columnas_temporales = [
    "id_falla",
    "estado_normalizado",
    "fecha_termino_dt",
    "intervalo_documental_horas",
    "validacion_temporal"
]

faltantes = (
    set(columnas_temporales)
    - set(informes.columns)
)

if faltantes:

    raise ValueError(
        f"Variables temporales faltantes: {faltantes}"
    )


# ==========================================================
# 10. RECONSTRUIR CONJUNTO TEMPORAL
# ==========================================================

temporal = informes[
    columnas_temporales
].copy()

temporal["estado_analisis"] = (
    temporal["estado_normalizado"]
    .astype("string")
    .str.strip()
    .str.upper()
)

temporal["intervalo_horas"] = pd.to_numeric(
    temporal["intervalo_documental_horas"],
    errors="coerce"
)

temporal["fecha_fin_disponible"] = (
    pd.to_datetime(
        temporal["fecha_termino_dt"],
        errors="coerce",
        format="mixed"
    ).notna()
)

temporal["intervalo_elegible"] = (
    temporal["estado_analisis"].eq("FINALIZADO")
    &
    temporal["validacion_temporal"].eq(
        "INTERVALO_NO_NEGATIVO"
    )
    &
    temporal["fecha_fin_disponible"]
    &
    temporal["intervalo_horas"].ge(0)
).fillna(False)


# ==========================================================
# 11. VALIDAR INTERVALOS DOCUMENTALES
# ==========================================================

assert int(
    temporal["intervalo_elegible"].sum()
) == 954, (
    "Los intervalos elegibles no coinciden con F2."
)

assert temporal.loc[
    temporal["intervalo_elegible"],
    "intervalo_horas"
].ge(0).all()

print(
    "[OK] 954 informes únicos con "
    "intervalos elegibles."
)


# ==========================================================
# 12. RECONSTRUIR ASOCIACIONES TEMPORALES
# ==========================================================

tiempos = (
    asociaciones[
        [
            "id_falla",
            "codigo_comuna"
        ]
    ]
    .merge(
        temporal[
            [
                "id_falla",
                "intervalo_horas",
                "intervalo_elegible"
            ]
        ],
        on="id_falla",
        how="left",
        validate="many_to_one"
    )
)

assert len(tiempos) == 1915

assert not tiempos.duplicated(
    ["id_falla", "codigo_comuna"]
).any()

assert int(
    tiempos["intervalo_elegible"].sum()
) == 980

print(
    "[OK] 980 asociaciones temporales elegibles."
)


# ==========================================================
# 13. INSTANCIAR NÚCLEO ORIENTADO A OBJETOS
# ==========================================================

nucleo = NucleoAnalitico(
    asociaciones=asociaciones,
    comunas=comunas,
    tiempos=tiempos,
    meses_observados=33
)


# ==========================================================
# 14. EJECUTAR DIMENSIONES ANALÍTICAS
# ==========================================================

resultados = nucleo.ejecutar()

frecuencia = resultados["frecuencia"]

recurrencia = resultados["recurrencia"]

duracion = resultados["duracion"]

assert len(frecuencia) == 15

assert len(duracion) == 15

assert frecuencia["codigo_comuna"].is_unique

assert duracion["codigo_comuna"].is_unique

print(
    "[OK] Frecuencia documental reproducida."
)

print(
    "[OK] Recurrencia causal reproducida."
)

print(
    "[OK] Duración documental reproducida."
)


# ==========================================================
# 15. RECONSTRUIR JERARQUÍA TERRITORIAL
# ==========================================================

columnas_asociaciones = [
    "id_falla",
    "codigo_comuna",
    "tipo_instalacion"
]

columnas_comunas = [
    "codigo_comuna",
    "region_oficial"
]

jerarquico = (
    asociaciones[
        columnas_asociaciones
    ]
    .merge(
        comunas[
            columnas_comunas
        ],
        on="codigo_comuna",
        how="left",
        validate="many_to_one"
    )
)

assert len(jerarquico) == 1915

assert jerarquico["region_oficial"].notna().all()

jerarquico["tipo_instalacion"] = (
    jerarquico["tipo_instalacion"]
    .astype("string")
    .str.strip()
    .fillna("SIN_DATO")
)

jerarquico.loc[
    jerarquico["tipo_instalacion"].eq(""),
    "tipo_instalacion"
] = "SIN_DATO"


# ==========================================================
# 16. AGRUPAR ESTRUCTURA JERÁRQUICA
# ==========================================================

agrupado = (
    jerarquico
    .groupby(
        [
            "region_oficial",
            "codigo_comuna",
            "tipo_instalacion"
        ],
        as_index=False
    )
    .agg(
        asociaciones=("id_falla", "size")
    )
)

assert int(
    agrupado["asociaciones"].sum()
) == 1915

arbol = construir_jerarquia(
    agrupado
)


# ==========================================================
# 17. VERIFICAR RECURSIVIDAD E ITERACIÓN
# ==========================================================

total_recursivo = (
    sumar_asociaciones_recursivo(arbol)
)

total_iterativo = (
    sumar_asociaciones_iterativo(arbol)
)

assert total_recursivo == 1915

assert total_iterativo == 1915

assert total_recursivo == total_iterativo

print(
    "[OK] Recursividad e iteración: "
    "1.915 asociaciones."
)


# ==========================================================
# 18. RECONSTRUIR PANEL ANALÍTICO
# ==========================================================

panel = construir_panel_integrado(
    frecuencia=frecuencia,
    recurrencia=recurrencia,
    duracion=duracion,
    asociaciones=asociaciones
)

assert len(panel) == 15

assert panel["codigo_comuna"].is_unique

assert int(
    panel["asociaciones_documentales"].sum()
) == 1915

assert int(
    panel["informes_validos"].sum()
) == 980

assert panel[
    "cobertura_temporal_pct"
].dropna().between(0, 100).all()

print(
    "[OK] Panel analítico de 15 comunas reconstruido."
)


# ==========================================================
# 19. LOCALIZAR PANEL ORIGINAL DE F3
# ==========================================================

ruta_original = (
    CARPETA_RESULTADOS
    / "F3_701_Panel_Integrado_Comunal.csv"
)

if not ruta_original.is_file():

    raise FileNotFoundError(
        "No se encontró el panel del apartado 7.1."
    )

panel_original = pd.read_csv(
    ruta_original,
    encoding="utf-8-sig",
    dtype={
        "codigo_comuna": "string"
    }
)


# ==========================================================
# 20. PREPARAR COMPARACIÓN DE PANELES
# ==========================================================

panel_reproducido = panel.copy()

panel_reproducido["codigo_comuna"] = (
    panel_reproducido["codigo_comuna"]
    .astype("string")
)

panel_original["codigo_comuna"] = (
    panel_original["codigo_comuna"]
    .astype("string")
)

assert set(
    panel_reproducido.columns
) == set(
    panel_original.columns
), (
    "Los paneles presentan columnas diferentes."
)

assert panel_original[
    "codigo_comuna"
].is_unique

columnas_comparacion = sorted(
    panel_original.columns.tolist()
)

panel_reproducido = (
    panel_reproducido
    .sort_values("codigo_comuna")
    [columnas_comparacion]
    .reset_index(drop=True)
)

panel_original = (
    panel_original
    .sort_values("codigo_comuna")
    [columnas_comparacion]
    .reset_index(drop=True)
)


# ==========================================================
# 21. COMPROBAR EQUIVALENCIA ANALÍTICA
# ==========================================================

pd.testing.assert_frame_equal(
    panel_reproducido,
    panel_original,
    check_dtype=False,
    check_exact=False,
    rtol=1e-9,
    atol=1e-8
)

print(
    "[OK] Panel reproducido equivalente "
    "al resultado del apartado 7.1."
)


# ==========================================================
# 22. EXPORTAR PANEL REPRODUCIDO
# ==========================================================

ruta_reproducida = (
    CARPETA_RESULTADOS
    / "F3_803_Panel_Reproducido.csv"
)

panel.to_csv(
    ruta_reproducida,
    index=False,
    encoding="utf-8-sig",
    lineterminator="\n"   # mismo archivo en Windows y Linux (D-04)
)

assert ruta_reproducida.is_file()


# ==========================================================
# 23. REGISTRAR ENTORNO Y TRAZABILIDAD
# ==========================================================

entorno = {
    "proyecto": "MCDI500 - Grupo 7",
    "fase": "F3",
    "python": sys.version.split()[0],
    "pandas": pd.__version__,
    "informes_unicos": len(informes),
    "asociaciones_documentales": len(asociaciones),
    "comunas": len(comunas),
    "intervalos_unicos_elegibles": int(
        temporal["intervalo_elegible"].sum()
    ),
    "asociaciones_temporales_elegibles": int(
        tiempos["intervalo_elegible"].sum()
    ),
    "panel_analitico_equivalente": True,
    "integridad_sha256_confirmada":
        integridad_binaria_confirmada,
    "estados_sha256": sorted(estados_sha)
}

ruta_entorno = (
    CARPETA_RESULTADOS
    / "F3_803_Entorno_Reproducibilidad.json"
)

ruta_entorno.write_text(
    json.dumps(
        entorno,
        ensure_ascii=False,
        indent=4
    ),
    encoding="utf-8"
)


# ==========================================================
# 24. PRESENTAR RESULTADOS
# ==========================================================

print()
print("=" * 65)
print("FASE 3 - REPRODUCIBILIDAD INDEPENDIENTE")
print("=" * 65)

print(
    "Informes únicos:",
    len(informes)
)

print(
    "Asociaciones documentales:",
    len(asociaciones)
)

print(
    "Comunas:",
    len(comunas)
)

print(
    "Informes con intervalos elegibles:",
    int(temporal["intervalo_elegible"].sum())
)

print(
    "Asociaciones temporales elegibles:",
    int(tiempos["intervalo_elegible"].sum())
)

print()
print("[OK] Datos cargados directamente desde F2.")
print("[OK] Módulos independientes ejecutados.")
print("[OK] Variables temporales reconstruidas.")
print("[OK] Algoritmos jerárquicos verificados.")
print("[OK] Indicadores analíticos reproducidos.")
print("[OK] Panel integrado equivalente.")

if integridad_binaria_confirmada:

    print(
        "[OK] Integridad SHA-256 confirmada."
    )

else:

    print(
        "[PENDIENTE] Aclarar diferencias "
        "SHA-256 registradas en la auditoría."
    )

print()
print(
    "[OK] Reproducibilidad funcional "
    "del núcleo verificada."
)

