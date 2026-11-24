"""
Incertidumbre de los indicadores comunales (F4).

Responde a la sugerencia de prioridad alta de la retroalimentación de F3:
las tasas y las medianas se calculan sobre pocos registros en varias
comunas, por lo que cada valor se acompaña de un intervalo de confianza.

- Tasas por 100.000 habitantes-año: intervalo exacto de Poisson sobre el
  conteo de informes no anulados (Garwood, 1936).
- Medianas de los intervalos documentales: intervalo bootstrap por
  percentiles, con semilla fija para que el resultado sea reproducible.
- Comunas con menos de 30 intervalos elegibles: baja precisión.

El módulo no usa SciPy: el intervalo de Poisson se obtiene por bisección
sobre la función de distribución, calculada con la biblioteca estándar.
"""

import math

import numpy as np
import pandas as pd

from src.indicadores import verificar_columnas

UMBRAL_BAJA_PRECISION = 30


# ==========================================================
# 1. INTERVALO EXACTO DE POISSON
# ==========================================================

def _cdf_poisson(k, media):
    """Probabilidad P(X <= k) para X ~ Poisson(media)."""

    if media == 0:
        return 1.0

    # Suma en escala logarítmica para evitar desbordes con conteos altos.
    log_terminos = [
        -media + i * math.log(media) - math.lgamma(i + 1)
        for i in range(k + 1)
    ]
    maximo = max(log_terminos)
    total = sum(math.exp(t - maximo) for t in log_terminos)

    return min(1.0, math.exp(maximo) * total)


def _biseccion(funcion, inferior, superior, iteraciones=200):
    """Raíz de una función monótona decreciente en [inferior, superior]."""

    for _ in range(iteraciones):
        medio = (inferior + superior) / 2
        if funcion(medio) > 0:
            inferior = medio
        else:
            superior = medio

    return (inferior + superior) / 2


def intervalo_poisson_exacto(conteo, nivel=0.95):
    """
    Intervalo de confianza exacto para la media de un conteo de Poisson.

    Devuelve (limite_inferior, limite_superior) del número esperado de
    informes. Con conteo cero, el límite inferior es exactamente cero.
    """

    if not isinstance(conteo, (int, np.integer)) or conteo < 0:
        raise ValueError("El conteo debe ser un entero no negativo.")

    if not 0 < nivel < 1:
        raise ValueError("El nivel de confianza debe estar entre 0 y 1.")

    conteo = int(conteo)
    alfa = 1 - nivel
    techo = conteo + 20 * math.sqrt(conteo + 1) + 20

    # Límite superior: P(X <= conteo | media) = alfa / 2.
    superior = _biseccion(
        lambda media: _cdf_poisson(conteo, media) - alfa / 2,
        0.0,
        techo
    )

    if conteo == 0:
        return 0.0, superior

    # Límite inferior: P(X >= conteo | media) = alfa / 2,
    # es decir, P(X <= conteo - 1 | media) = 1 - alfa / 2.
    inferior = _biseccion(
        lambda media: _cdf_poisson(conteo - 1, media) - (1 - alfa / 2),
        0.0,
        techo
    )

    return inferior, superior


def frecuencia_con_intervalo(panel, meses_observados=33, nivel=0.95):
    """
    Agrega el intervalo de confianza a la frecuencia documental normalizada.

    Usa la misma fórmula de F3 (informes no anulados / población
    * 100.000 / años observados) aplicada a los dos límites del conteo.
    """

    verificar_columnas(
        panel,
        ["codigo_comuna", "comuna_oficial", "poblacion_2024",
         "informes_no_anulados"],
        "panel"
    )

    if meses_observados <= 0:
        raise ValueError("El período de observación debe ser positivo.")

    anios = meses_observados / 12
    resultado = panel[
        ["codigo_comuna", "comuna_oficial", "poblacion_2024",
         "informes_no_anulados"]
    ].copy()

    escala = 100_000 / (resultado["poblacion_2024"] * anios)
    limites = resultado["informes_no_anulados"].apply(
        lambda n: intervalo_poisson_exacto(int(n), nivel)
    )

    resultado["frecuencia_100k_hab_anio"] = (
        resultado["informes_no_anulados"] * escala
    )
    resultado["ic_inferior"] = limites.str[0] * escala
    resultado["ic_superior"] = limites.str[1] * escala

    columnas = ["frecuencia_100k_hab_anio", "ic_inferior", "ic_superior"]
    resultado[columnas] = resultado[columnas].round(2)

    return (
        resultado
        .sort_values("frecuencia_100k_hab_anio", ascending=False)
        .reset_index(drop=True)
    )


# ==========================================================
# 2. INTERVALO BOOTSTRAP DE LA MEDIANA
# ==========================================================

def intervalo_bootstrap_mediana(valores, repeticiones=2000, nivel=0.95,
                                semilla=500):
    """
    Intervalo bootstrap por percentiles para la mediana.

    Remuestrea los valores con reposición, calcula la mediana de cada
    muestra y toma los percentiles alfa/2 y 1 - alfa/2. Sin valores
    devuelve (NaN, NaN); con uno solo, el intervalo colapsa a ese valor.
    """

    datos = np.asarray(pd.Series(valores).dropna(), dtype=float)

    if repeticiones < 1:
        raise ValueError("Las repeticiones deben ser al menos una.")

    if datos.size == 0:
        return float("nan"), float("nan")

    if datos.size == 1:
        return float(datos[0]), float(datos[0])

    generador = np.random.default_rng(semilla)
    indices = generador.integers(0, datos.size,
                                 size=(repeticiones, datos.size))
    medianas = np.median(datos[indices], axis=1)
    alfa = 1 - nivel

    return (float(np.quantile(medianas, alfa / 2)),
            float(np.quantile(medianas, 1 - alfa / 2)))


def marcar_baja_precision(cantidad, umbral=UMBRAL_BAJA_PRECISION):
    """True si la cantidad de registros es menor que el umbral."""

    if cantidad < 0:
        raise ValueError("La cantidad no puede ser negativa.")

    return cantidad < umbral


def seleccionar_intervalos_elegibles(asociaciones):
    """
    Reproduce el criterio de elegibilidad temporal de F3.

    Elegible = informe FINALIZADO, validación INTERVALO_NO_NEGATIVO,
    fecha de término disponible e intervalo mayor o igual que cero.
    """

    verificar_columnas(
        asociaciones,
        ["id_falla", "codigo_comuna", "comuna_oficial",
         "estado_normalizado", "validacion_temporal", "fecha_termino_dt",
         "intervalo_documental_horas"],
        "asociaciones"
    )

    datos = asociaciones.copy()
    datos["intervalo_horas"] = pd.to_numeric(
        datos["intervalo_documental_horas"], errors="coerce"
    )
    fecha_fin = pd.to_datetime(
        datos["fecha_termino_dt"], errors="coerce", format="mixed"
    )

    elegible = (
        datos["estado_normalizado"].astype("string").str.strip()
        .str.upper().eq("FINALIZADO")
        & datos["validacion_temporal"].eq("INTERVALO_NO_NEGATIVO")
        & fecha_fin.notna()
        & datos["intervalo_horas"].ge(0)
    ).fillna(False)

    return datos.loc[elegible, ["id_falla", "codigo_comuna",
                                "comuna_oficial", "intervalo_horas"]]


def duracion_con_intervalo(asociaciones, repeticiones=2000, nivel=0.95,
                           semilla=500, umbral=UMBRAL_BAJA_PRECISION):
    """
    Mediana de los intervalos elegibles por comuna, con su intervalo
    bootstrap y la marca de baja precisión.
    """

    elegibles = seleccionar_intervalos_elegibles(asociaciones)
    filas = []

    for (codigo, comuna), grupo in elegibles.groupby(
            ["codigo_comuna", "comuna_oficial"]):
        valores = grupo["intervalo_horas"]
        inferior, superior = intervalo_bootstrap_mediana(
            valores, repeticiones, nivel, semilla
        )
        # Un mismo conteo para la columna publicada y para la marca de
        # precisión (cada vínculo informe-comuna es único en la comuna).
        elegibles = int(grupo["id_falla"].nunique())
        filas.append({
            "codigo_comuna": codigo,
            "comuna_oficial": comuna,
            "intervalos_elegibles": elegibles,
            "mediana_horas": float(valores.median()),
            "percentil_75_horas": float(valores.quantile(0.75)),
            "ic_inferior": inferior,
            "ic_superior": superior,
            "baja_precision": marcar_baja_precision(elegibles, umbral),
        })

    resultado = pd.DataFrame(filas)
    columnas = ["mediana_horas", "percentil_75_horas",
                "ic_inferior", "ic_superior"]
    resultado[columnas] = resultado[columnas].round(2)

    return (
        resultado
        .sort_values("mediana_horas", ascending=False)
        .reset_index(drop=True)
    )


# ==========================================================
# 3. COMPARACIÓN ENTRE COMUNAS
# ==========================================================

def se_superponen(a_inferior, a_superior, b_inferior, b_superior):
    """True si dos intervalos comparten al menos un punto."""

    return a_inferior <= b_superior and b_inferior <= a_superior


def pares_no_distinguibles(tabla, columna_nombre="comuna_oficial"):
    """
    Lista los pares de comunas vecinas en el ranking cuyos intervalos se
    superponen. Para esos pares, el informe debe decir que no se
    distinguen.
    """

    verificar_columnas(
        tabla, [columna_nombre, "ic_inferior", "ic_superior"], "tabla"
    )

    filas = tabla.reset_index(drop=True)
    pares = []

    for i in range(len(filas) - 1):
        actual, siguiente = filas.iloc[i], filas.iloc[i + 1]
        if se_superponen(actual["ic_inferior"], actual["ic_superior"],
                         siguiente["ic_inferior"], siguiente["ic_superior"]):
            pares.append((actual[columna_nombre], siguiente[columna_nombre]))

    return pares
