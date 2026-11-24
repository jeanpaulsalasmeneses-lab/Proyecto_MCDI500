"""
Sensibilidad de la lectura conjunta a Antofagasta (F4).

Responde al punto 3 de la retroalimentación de F3 (issue #58): Antofagasta
concentra la mayor frecuencia, asociada a desconexiones por fallas en
instalaciones de terceros. Hay que revisar si ese patrón depende de pocas
instalaciones o de un período acotado, y mostrar el panel con y sin esa
comuna para que no domine la lectura de las 15 comunas.

Tres preguntas, una función cada una:

- ¿Pocas instalaciones?  concentracion_por_comuna(): qué parte de los
  informes de cada comuna viene de su subestación o empresa más frecuente
  y de las cinco más frecuentes.
- ¿Un período acotado?    informes_por_anio(): frecuencia anualizada y
  puesto de cada comuna en 2024, 2025 y 2026 (enero a septiembre).
- ¿Domina la lectura?     resumen_con_y_sin(): los indicadores agregados
  de las 15 comunas, con y sin una comuna.

Las cifras son descriptivas: dicen con qué frecuencia aparece algo en los
informes del CEN, no por qué ocurre.
"""

import pandas as pd

from src.causas import cargar_equivalencias_causas, normalizar_descripcion_causa
from src.incertidumbre import seleccionar_intervalos_elegibles
from src.indicadores import calcular_recurrencia_comunal, verificar_columnas

# Meses observados de cada año (el período termina en septiembre de 2026).
MESES_POR_ANIO = {2024: 12, 2025: 12, 2026: 9}


# ==========================================================
# 0. PREPARACIÓN
# ==========================================================

def no_anulados(asociaciones):
    """Vínculos informe-comuna cuyo estado no es ANULADO (como F3)."""

    verificar_columnas(asociaciones, ["estado_normalizado"], "asociaciones")
    estado = asociaciones["estado_normalizado"].astype("string").str.strip().str.upper()
    return asociaciones.loc[estado.ne("ANULADO")].copy()


def unir_instalaciones(asociaciones, eventos,
                       columnas=("SubEstación", "Empresa")):
    """
    Agrega a cada vínculo la subestación y la empresa del informe.

    Las asociaciones de F2 no traen esas columnas. Se toman del consolidado
    del CEN (un registro por id_falla) sin modificar ninguno de los dos.
    """

    columnas = list(columnas)
    verificar_columnas(asociaciones, ["id_falla", "comuna_oficial"], "asociaciones")
    verificar_columnas(eventos, ["id_falla", *columnas], "eventos")

    if eventos["id_falla"].duplicated().any():
        raise ValueError("El consolidado de eventos repite id_falla.")

    unidas = asociaciones.merge(eventos[["id_falla", *columnas]], on="id_falla",
                                how="left", validate="many_to_one")
    if len(unidas) != len(asociaciones):
        raise ValueError("La unión cambió el número de vínculos.")
    return unidas


# ==========================================================
# 1. ¿POCAS INSTALACIONES?
# ==========================================================

def concentracion_por_comuna(datos, columna, top=5):
    """
    Concentración de los informes de cada comuna en `columna`.

    Por comuna devuelve: informes únicos, informes con dato en la columna,
    cuántos valores distintos hay, el más frecuente y qué porcentaje de los
    informes con dato reúnen el primero y los `top` primeros.

    Los informes sin dato (por ejemplo, una falla de línea no tiene
    subestación) no entran en los porcentajes, pero se informan.
    """

    if top < 1:
        raise ValueError("top debe ser al menos 1.")
    verificar_columnas(datos, ["id_falla", "comuna_oficial", columna], "datos")

    filas = []
    for comuna, grupo in datos.groupby("comuna_oficial"):
        con_dato = grupo.dropna(subset=[columna])
        conteo = (con_dato.groupby(columna)["id_falla"].nunique()
                  .sort_values(ascending=False, kind="mergesort"))
        n_dato = con_dato["id_falla"].nunique()
        filas.append({
            "comuna_oficial": comuna,
            "informes": grupo["id_falla"].nunique(),
            "informes_con_dato": n_dato,
            "distintos": int(conteo.size),
            "principal": conteo.index[0] if conteo.size else None,
            "pct_principal": round(100 * conteo.iloc[0] / n_dato, 1) if n_dato else float("nan"),
            f"pct_top{top}": round(100 * conteo.head(top).sum() / n_dato, 1) if n_dato else float("nan"),
        })

    return (pd.DataFrame(filas)
            .sort_values(f"pct_top{top}", ascending=False, kind="mergesort")
            .reset_index(drop=True))


# ==========================================================
# 2. ¿UN PERÍODO ACOTADO?
# ==========================================================

def informes_por_anio(datos, panel, meses_por_anio=None):
    """
    Informes únicos por comuna y año, con su frecuencia anualizada
    (por 100.000 habitantes-año) y el puesto de la comuna en cada año.

    La frecuencia se anualiza con los meses observados de cada año, para
    que 2026 (nueve meses) sea comparable con 2024 y 2025.
    """

    meses_por_anio = meses_por_anio or MESES_POR_ANIO
    verificar_columnas(datos, ["id_falla", "comuna_oficial", "fecha_perturbacion_dt"], "datos")
    verificar_columnas(panel, ["comuna_oficial", "poblacion_2024"], "panel")

    if any(m <= 0 for m in meses_por_anio.values()):
        raise ValueError("Los meses observados deben ser positivos.")

    anio = pd.to_datetime(datos["fecha_perturbacion_dt"], errors="coerce",
                          format="mixed").dt.year
    if anio.isna().any():
        raise ValueError("Existen vínculos sin fecha de perturbación.")
    fuera = set(anio.unique()) - set(meses_por_anio)
    if fuera:
        raise ValueError(f"Años sin meses observados declarados: {sorted(fuera)}")

    conteo = (datos.assign(anio=anio.astype(int))
              .groupby(["comuna_oficial", "anio"])["id_falla"].nunique()
              .rename("informes").reset_index())

    # Todas las combinaciones comuna × año, con cero donde no hay informes.
    completo = pd.MultiIndex.from_product(
        [panel["comuna_oficial"], sorted(meses_por_anio)],
        names=["comuna_oficial", "anio"])
    tabla = (conteo.set_index(["comuna_oficial", "anio"]).reindex(completo, fill_value=0)
             .reset_index()
             .merge(panel[["comuna_oficial", "poblacion_2024"]], on="comuna_oficial",
                    how="left", validate="many_to_one"))

    tabla["meses_observados"] = tabla["anio"].map(meses_por_anio)
    tabla["frecuencia_100k_hab_anio"] = (
        tabla["informes"] / tabla["poblacion_2024"] * 100_000
        / (tabla["meses_observados"] / 12)
    ).round(2)
    tabla["puesto"] = (tabla.groupby("anio")["frecuencia_100k_hab_anio"]
                       .rank(ascending=False, method="min").astype(int))

    return tabla.drop(columns="poblacion_2024")


# ==========================================================
# 3. ¿DOMINA LA LECTURA CONJUNTA?
# ==========================================================

def _indicadores_agregados(asociaciones, panel, meses_observados):
    """Indicadores de un conjunto de comunas, tomado como un todo."""

    validas = no_anulados(asociaciones)
    anios = meses_observados / 12

    # Descripción causal determinada más frecuente, con el mismo criterio
    # de F3 (excluye «Se investiga», «SIN_DATO», etc.), sobre informes únicos.
    unicos = asociaciones.drop_duplicates("id_falla").assign(
        codigo_comuna="TOTAL", comuna_oficial="TOTAL")
    # Errores de escritura del CEN corregidos con la tabla versionada (D-15).
    unicos["descripcion_causa"] = normalizar_descripcion_causa(
        unicos["descripcion_causa"], cargar_equivalencias_causas())
    recurrencia = calcular_recurrencia_comunal(unicos, cantidad=1)
    principal = recurrencia.iloc[0]

    elegibles = seleccionar_intervalos_elegibles(asociaciones).drop_duplicates("id_falla")

    return {
        "Comunas": len(panel),
        "Población 2024": int(panel["poblacion_2024"].sum()),
        "Informes únicos no anulados": int(validas["id_falla"].nunique()),
        "Vínculos informe-comuna no anulados": int(len(validas)),
        "Frecuencia agregada (vínculos por 100.000 hab.-año)": round(
            panel["informes_no_anulados"].sum() / panel["poblacion_2024"].sum()
            * 100_000 / anios, 2),
        "Promedio de las frecuencias comunales": round(
            panel["frecuencia_100k_hab_anio"].mean(), 2),
        "Descripción causal determinada más frecuente": principal["descripcion_causa"],
        "Participación de esa descripción (% de informes únicos)": round(
            float(principal["porcentaje_comunal"]), 2),
        "Intervalos documentales elegibles (informes únicos)": int(len(elegibles)),
        "Mediana del intervalo documental (horas)": round(
            float(elegibles["intervalo_horas"].median()), 2),
    }


def resumen_con_y_sin(asociaciones, panel, excluir, meses_observados=33):
    """
    Indicadores agregados de todas las comunas y sin la comuna `excluir`.

    Devuelve una tabla con una fila por indicador y dos columnas, para que
    se vea cuánto cambia la lectura conjunta sin esa comuna.
    """

    verificar_columnas(asociaciones, ["comuna_oficial"], "asociaciones")
    verificar_columnas(panel, ["comuna_oficial", "poblacion_2024",
                               "informes_no_anulados", "frecuencia_100k_hab_anio"], "panel")
    if excluir not in set(panel["comuna_oficial"]):
        raise ValueError(f"La comuna «{excluir}» no está en el panel.")

    todas = _indicadores_agregados(asociaciones, panel, meses_observados)
    sin = _indicadores_agregados(
        asociaciones.loc[asociaciones["comuna_oficial"].ne(excluir)],
        panel.loc[panel["comuna_oficial"].ne(excluir)],
        meses_observados)

    return pd.DataFrame({"indicador": list(todas),
                         f"{len(panel)} comunas": list(todas.values()),
                         f"sin {excluir}": list(sin.values())})
