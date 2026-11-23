"""
Dimensión temporal de los informes comunales (F4).

Responde a la sugerencia 2 de la retroalimentación de F3: mostrar la
evolución mensual de los informes por comuna en los 33 meses observados
(enero de 2024 a septiembre de 2026) e identificar meses atípicos, como el
apagón nacional del 25-02-2025, junto con los indicadores con y sin ese
episodio.

La unidad que se cuenta es el informe no anulado distinto (id_falla) por
comuna, la misma del indicador de frecuencia de F3.
"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import PowerNorm

from src.indicadores import verificar_columnas

FECHA_APAGON = pd.Timestamp("2025-02-25")
PERIODO_INICIO = pd.Period("2024-01", freq="M")
PERIODO_FIN = pd.Period("2026-09", freq="M")
MESES_ES = ["ene", "feb", "mar", "abr", "may", "jun",
            "jul", "ago", "sep", "oct", "nov", "dic"]


def _preparar(asociaciones, excluir_anulados=True):
    """Valida columnas, excluye anulados y agrega la fecha y el mes."""

    verificar_columnas(
        asociaciones,
        ["id_falla", "comuna_oficial", "estado_normalizado",
         "fecha_perturbacion_dt"],
        "asociaciones"
    )

    datos = asociaciones.copy()
    datos["estado_normalizado"] = (
        datos["estado_normalizado"].astype("string").str.strip().str.upper()
    )

    if excluir_anulados:
        datos = datos.loc[datos["estado_normalizado"].ne("ANULADO")].copy()

    datos["fecha"] = pd.to_datetime(
        datos["fecha_perturbacion_dt"], errors="coerce", format="mixed"
    )

    if datos["fecha"].isna().any():
        raise ValueError("Existen informes sin fecha de perturbación.")

    datos["mes"] = datos["fecha"].dt.to_period("M")

    return datos


def contar_informes_mensuales(asociaciones, excluir_anulados=True,
                              inicio=PERIODO_INICIO, fin=PERIODO_FIN,
                              orden_comunas=None):
    """
    Matriz comuna × mes con la cantidad de informes distintos.

    Los meses sin informes quedan con cero, de modo que la matriz siempre
    tiene todas las columnas del período observado.
    """

    datos = _preparar(asociaciones, excluir_anulados)

    if datos["mes"].lt(inicio).any() or datos["mes"].gt(fin).any():
        raise ValueError("Existen informes fuera del período observado.")

    matriz = datos.pivot_table(
        index="comuna_oficial",
        columns="mes",
        values="id_falla",
        aggfunc="nunique",
        fill_value=0
    )

    meses = pd.period_range(inicio, fin, freq="M")
    matriz = matriz.reindex(columns=meses, fill_value=0).astype(int)
    matriz.columns.name = "mes"

    if orden_comunas is not None:
        faltantes = set(matriz.index) - set(orden_comunas)
        if faltantes:
            raise ValueError(f"Comunas sin posición en el orden: {faltantes}")
        matriz = matriz.reindex(orden_comunas, fill_value=0)

    return matriz


def peso_de_un_dia(asociaciones, fecha=FECHA_APAGON, panel=None,
                   meses_observados=33):
    """
    Cuánto pesa un solo día en los informes de cada comuna.

    Devuelve, por comuna, los informes no anulados totales, los de ese
    día y su porcentaje. Si se entrega el panel de F3 (con población), agrega
    la frecuencia por 100.000 habitantes-año con y sin ese día y el puesto
    en el ranking en cada caso.
    """

    datos = _preparar(asociaciones)
    dia = datos["fecha"].dt.normalize().eq(pd.Timestamp(fecha).normalize())

    totales = datos.groupby("comuna_oficial")["id_falla"].nunique()
    del_dia = datos.loc[dia].groupby("comuna_oficial")["id_falla"].nunique()

    tabla = pd.DataFrame({
        "informes_total": totales,
        "informes_del_dia": del_dia
    }).fillna(0).astype(int)
    tabla["informes_sin_dia"] = tabla["informes_total"] - tabla["informes_del_dia"]
    tabla["pct_del_dia"] = (
        tabla["informes_del_dia"] / tabla["informes_total"] * 100
    ).round(1)

    if panel is not None:
        verificar_columnas(panel, ["comuna_oficial", "poblacion_2024"], "panel")
        anios = meses_observados / 12
        poblacion = panel.set_index("comuna_oficial")["poblacion_2024"]
        escala = 100_000 / (poblacion.reindex(tabla.index) * anios)
        tabla["frecuencia_total"] = (tabla["informes_total"] * escala).round(2)
        tabla["frecuencia_sin_dia"] = (tabla["informes_sin_dia"] * escala).round(2)
        tabla["puesto_total"] = (
            tabla["frecuencia_total"].rank(ascending=False, method="min")
            .astype(int)
        )
        tabla["puesto_sin_dia"] = (
            tabla["frecuencia_sin_dia"].rank(ascending=False, method="min")
            .astype(int)
        )
        tabla = tabla.sort_values("frecuencia_total", ascending=False)
    else:
        tabla = tabla.sort_values("pct_del_dia", ascending=False)

    return tabla.reset_index().rename(columns={"index": "comuna_oficial"})


def graficar_mapa_calor(matriz, titulo, subtitulo=None, mes_destacado=None,
                        ruta_salida=None, fuente=None, gamma=0.5):
    """
    Dibuja la matriz comuna × mes como mapa de calor.

    La escala de color usa una potencia (gamma < 1) para que los meses con
    pocos informes no queden todos del mismo color frente al pico; la barra
    de color sigue mostrando los conteos reales. La paleta cividis es apta
    para daltonismo.
    """

    if matriz.empty:
        raise ValueError("La matriz está vacía.")

    fig, ax = plt.subplots(figsize=(14, 6.4))
    imagen = ax.imshow(
        matriz.to_numpy(),
        aspect="auto",
        cmap="cividis",
        norm=PowerNorm(gamma=gamma, vmin=0, vmax=matriz.to_numpy().max())
    )

    meses = list(matriz.columns)
    etiquetas = [f"{MESES_ES[m.month - 1]} {m.year}"
                 if m.month in (1, 4, 7, 10) else "" for m in meses]
    ax.set_xticks(range(len(meses)))
    ax.set_xticklabels(etiquetas, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(matriz.index)))
    ax.set_yticklabels(matriz.index, fontsize=10)
    ax.set_xlabel("Mes de perturbación")

    # Líneas suaves entre celdas para leer filas y columnas.
    ax.set_xticks([x - 0.5 for x in range(1, len(meses))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(matriz.index))], minor=True)
    ax.grid(which="minor", color="white", linewidth=0.6)
    ax.tick_params(which="minor", length=0)

    if mes_destacado is not None:
        posicion = meses.index(pd.Period(mes_destacado, freq="M"))
        ax.add_patch(plt.Rectangle(
            (posicion - 0.5, -0.5), 1, len(matriz.index),
            fill=False, edgecolor="#d62728", linewidth=2.2
        ))
        ax.text(posicion + 0.8, -0.85, "← apagón nacional del 25-02-2025",
                fontsize=9.5, color="#d62728", ha="left", va="center",
                clip_on=False)

    barra = fig.colorbar(imagen, ax=ax, pad=0.015)
    barra.set_label("Informes no anulados distintos en el mes")

    fig.suptitle(titulo, x=0.01, ha="left", fontsize=14, fontweight="bold")
    if subtitulo:
        ax.set_title(subtitulo, loc="left", fontsize=10.5, color="#444444",
                     pad=22)
    if fuente:
        fig.text(0.01, 0.005, fuente, fontsize=8.5, color="#555555")

    fig.tight_layout(rect=(0, 0.03, 1, 0.97))

    if ruta_salida is not None:
        fig.savefig(ruta_salida, dpi=200, bbox_inches="tight")

    return fig
