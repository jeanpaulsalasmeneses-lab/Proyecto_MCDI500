"""
Indicadores comunales del núcleo algorítmico (Fase 3).

Frecuencia documental normalizada por población, recurrencia causal y
duración documental por comuna, y su integración en un panel de 15 comunas.
Funciones sin estado: no aprenden nada de los datos, por eso no son clases.
"""

import pandas as pd


def verificar_columnas(df, columnas, nombre):
    """
    Comprueba la disponibilidad de las columnas
    necesarias para ejecutar una función.
    """

    faltantes = set(columnas) - set(df.columns)

    if faltantes:
        raise ValueError(
            f"Columnas faltantes en {nombre}: "
            f"{sorted(faltantes)}"
        )


def calcular_frecuencia_comunal(
    asociaciones,
    comunas,
    meses_observados=33
):
    """
    Calcula informes no anulados por comuna y
    su frecuencia documental normalizada.

    La población es un denominador contextual.
    No representa clientes eléctricos afectados.
    """

    if meses_observados <= 0:
        raise ValueError(
            "El período de observación debe ser positivo."
        )

    verificar_columnas(
        asociaciones,
        [
            "id_falla",
            "codigo_comuna",
            "estado_normalizado"
        ],
        "asociaciones"
    )

    verificar_columnas(
        comunas,
        [
            "codigo_comuna",
            "comuna_oficial",
            "poblacion_2024"
        ],
        "comunas"
    )

    # Preparar asociaciones documentales.

    datos = asociaciones[
        [
            "id_falla",
            "codigo_comuna",
            "estado_normalizado"
        ]
    ].copy()

    if datos.duplicated(
        ["id_falla", "codigo_comuna"]
    ).any():
        raise ValueError(
            "Existen asociaciones informe-comuna duplicadas."
        )

    datos["estado_normalizado"] = (
        datos["estado_normalizado"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    if datos["estado_normalizado"].isna().any():
        raise ValueError(
            "Existen informes sin estado administrativo."
        )

    # Excluir anulados del indicador principal.

    datos = datos.loc[
        datos["estado_normalizado"].ne("ANULADO")
    ].copy()

    # Contar informes distintos por comuna.

    conteos = (
        datos.groupby(
            "codigo_comuna",
            as_index=False
        )
        .agg(
            informes_no_anulados=("id_falla", "nunique")
        )
    )

    # Preparar maestro comunal.

    maestro = comunas[
        [
            "codigo_comuna",
            "comuna_oficial",
            "poblacion_2024"
        ]
    ].copy()

    maestro["poblacion_2024"] = pd.to_numeric(
        maestro["poblacion_2024"],
        errors="coerce"
    )

    if (
        maestro["codigo_comuna"].duplicated().any()
        or maestro["poblacion_2024"].isna().any()
        or maestro["poblacion_2024"].le(0).any()
    ):
        raise ValueError(
            "El maestro comunal presenta datos inválidos."
        )

    if not datos["codigo_comuna"].isin(
        maestro["codigo_comuna"]
    ).all():
        raise ValueError(
            "Existen asociaciones con códigos no reconocidos."
        )

    # Conservar las 15 comunas, incluso con conteo cero.

    resultado = maestro.merge(
        conteos,
        on="codigo_comuna",
        how="left",
        validate="one_to_one"
    )

    resultado["informes_no_anulados"] = (
        resultado["informes_no_anulados"]
        .fillna(0)
        .astype(int)
    )

    anios_observados = meses_observados / 12

    resultado["frecuencia_100k_hab_anio"] = (
        resultado["informes_no_anulados"]
        / resultado["poblacion_2024"]
        * 100_000
        / anios_observados
    ).round(2)

    return (
        resultado
        .sort_values(
            "frecuencia_100k_hab_anio",
            ascending=False
        )
        .reset_index(drop=True)
    )


def calcular_recurrencia_comunal(
    asociaciones,
    cantidad=3
):
    """
    Identifica las descripciones causales más
    frecuentes de cada comuna.

    No interpreta las descripciones como
    mecanismos físicos independientes.
    """

    if cantidad < 1:
        raise ValueError(
            "La cantidad debe ser al menos uno."
        )

    verificar_columnas(
        asociaciones,
        [
            "id_falla",
            "codigo_comuna",
            "comuna_oficial",
            "descripcion_causa"
        ],
        "asociaciones"
    )

    datos = asociaciones[
        [
            "id_falla",
            "codigo_comuna",
            "comuna_oficial",
            "descripcion_causa"
        ]
    ].copy()

    if datos.duplicated(
        ["id_falla", "codigo_comuna"]
    ).any():
        raise ValueError(
            "Existen asociaciones duplicadas."
        )

    # Normalizar espacios sin alterar las denominaciones.

    datos["descripcion_causa"] = (
        datos["descripcion_causa"]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Identificar descripciones no determinadas.

    categorias_no_determinadas = {
        "",
        "SE INVESTIGA",
        "SIN_DATO",
        "SIN DATO",
        "SIN INFORMACIÓN",
        "SIN INFORMACION",
        "NO DETERMINADA",
        "NO DETERMINADO",
        "POR DETERMINAR",
        "PENDIENTE",
        "EN INVESTIGACIÓN",
        "EN INVESTIGACION"
    }

    clave_causal = (
        datos["descripcion_causa"]
        .str.upper()
        .str.rstrip(".")
    )

    mascara_valida = (
        clave_causal.notna()
        & ~clave_causal.isin(categorias_no_determinadas)
    )

    # Mantener únicamente descripciones específicas.

    datos_validos = datos.loc[
        mascara_valida
    ].copy()

    # Calcular frecuencia por comuna y descripción.

    recurrencias = (
        datos_validos
        .groupby(
            [
                "codigo_comuna",
                "comuna_oficial",
                "descripcion_causa"
            ],
            as_index=False
        )
        .agg(
            informes=("id_falla", "nunique")
        )
    )

    # Calcular denominador comunal completo.

    totales = (
        datos.groupby(
            "codigo_comuna",
            as_index=False
        )
        .agg(
            total_informes_comuna=("id_falla", "nunique")
        )
    )

    recurrencias = recurrencias.merge(
        totales,
        on="codigo_comuna",
        how="left",
        validate="many_to_one"
    )

    recurrencias["porcentaje_comunal"] = (
        recurrencias["informes"]
        / recurrencias["total_informes_comuna"]
        * 100
    ).round(2)

    # Ordenar por frecuencia.

    recurrencias = recurrencias.sort_values(
        [
            "comuna_oficial",
            "informes",
            "descripcion_causa"
        ],
        ascending=[True, False, True]
    )

    # Seleccionar las primeras categorías de cada comuna.

    resultado = (
        recurrencias
        .groupby("codigo_comuna", group_keys=False)
        .head(cantidad)
        .reset_index(drop=True)
    )

    return resultado


def calcular_duracion_comunal(
    tiempos,
    comunas
):
    """
    Calcula estadísticas de intervalos documentales.

    Considera solamente los informes previamente
    clasificados como elegibles.
    """

    verificar_columnas(
        tiempos,
        [
            "id_falla",
            "codigo_comuna",
            "intervalo_horas",
            "intervalo_elegible"
        ],
        "tiempos"
    )

    verificar_columnas(
        comunas,
        [
            "codigo_comuna",
            "comuna_oficial"
        ],
        "comunas"
    )

    datos = tiempos.copy()

    if datos.duplicated(
        ["id_falla", "codigo_comuna"]
    ).any():
        raise ValueError(
            "Existen asociaciones temporales duplicadas."
        )

    datos["intervalo_horas"] = pd.to_numeric(
        datos["intervalo_horas"],
        errors="coerce"
    )

    # Seleccionar intervalos elegibles.

    datos_validos = datos.loc[
        datos["intervalo_elegible"].fillna(False)
    ].copy()

    if (
        datos_validos["intervalo_horas"].isna().any()
        or datos_validos["intervalo_horas"].lt(0).any()
    ):
        raise ValueError(
            "Existen intervalos elegibles inválidos."
        )

    # Calcular estadísticas por comuna.

    resumen = (
        datos_validos
        .groupby(
            "codigo_comuna",
            as_index=False
        )
        .agg(
            informes_validos=("id_falla", "nunique"),

            mediana_horas=(
                "intervalo_horas",
                "median"
            ),

            percentil_75_horas=(
                "intervalo_horas",
                lambda x: x.quantile(0.75)
            )
        )
    )

    # Conservar todas las comunas.

    resultado = comunas[
        [
            "codigo_comuna",
            "comuna_oficial"
        ]
    ].merge(
        resumen,
        on="codigo_comuna",
        how="left",
        validate="one_to_one"
    )

    resultado["informes_validos"] = (
        resultado["informes_validos"]
        .fillna(0)
        .astype(int)
    )

    # Mantener NaN en estadísticas sin datos;
    # no imputar duraciones inexistentes.

    return (
        resultado
        .sort_values(
            "mediana_horas",
            ascending=False,
            na_position="last"
        )
        .reset_index(drop=True)
    )


def construir_panel_integrado(
    frecuencia,
    recurrencia,
    duracion,
    asociaciones
):
    """
    Integra los resultados analíticos de F3.

    Unidad final:
        Una fila por comuna.

    Conserva las diferencias entre los
    universos de frecuencia, recurrencia
    y duración documental.
    """

    # ------------------------------------------------------
    # Validar columnas requeridas
    # ------------------------------------------------------

    verificar_columnas(
        frecuencia,
        [
            "codigo_comuna",
            "comuna_oficial",
            "poblacion_2024",
            "informes_no_anulados",
            "frecuencia_100k_hab_anio"
        ],
        "frecuencia"
    )

    verificar_columnas(
        recurrencia,
        [
            "codigo_comuna",
            "descripcion_causa",
            "informes",
            "porcentaje_comunal"
        ],
        "recurrencia"
    )

    verificar_columnas(
        duracion,
        [
            "codigo_comuna",
            "informes_validos",
            "mediana_horas",
            "percentil_75_horas"
        ],
        "duracion"
    )

    verificar_columnas(
        asociaciones,
        [
            "id_falla",
            "codigo_comuna"
        ],
        "asociaciones"
    )

    # ------------------------------------------------------
    # Validar unicidad territorial
    # ------------------------------------------------------

    if frecuencia["codigo_comuna"].duplicated().any():
        raise ValueError(
            "Existen comunas duplicadas en frecuencia."
        )

    if duracion["codigo_comuna"].duplicated().any():
        raise ValueError(
            "Existen comunas duplicadas en duración."
        )

    if asociaciones.duplicated(
        ["id_falla", "codigo_comuna"]
    ).any():
        raise ValueError(
            "Existen asociaciones documentales duplicadas."
        )

    # ------------------------------------------------------
    # Construir conjunto base
    # ------------------------------------------------------

    panel = frecuencia[
        [
            "codigo_comuna",
            "comuna_oficial",
            "poblacion_2024",
            "informes_no_anulados",
            "frecuencia_100k_hab_anio"
        ]
    ].copy()

    # ------------------------------------------------------
    # Calcular asociaciones totales por comuna
    # ------------------------------------------------------

    totales = (
        asociaciones
        .groupby(
            "codigo_comuna",
            as_index=False
        )
        .agg(
            asociaciones_documentales=(
                "id_falla",
                "size"
            )
        )
    )

    panel = panel.merge(
        totales,
        on="codigo_comuna",
        how="left",
        validate="one_to_one"
    )

    panel["asociaciones_documentales"] = (
        panel["asociaciones_documentales"]
        .fillna(0)
        .astype(int)
    )

    # ------------------------------------------------------
    # Seleccionar la descripción causal más recurrente
    # ------------------------------------------------------

    causa_principal = (
        recurrencia
        .sort_values(
            [
                "codigo_comuna",
                "informes",
                "descripcion_causa"
            ],
            ascending=[True, False, True],
            kind="mergesort"
        )
        .drop_duplicates(
            subset=["codigo_comuna"],
            keep="first"
        )
        [
            [
                "codigo_comuna",
                "descripcion_causa",
                "informes",
                "porcentaje_comunal"
            ]
        ]
        .rename(
            columns={
                "descripcion_causa":
                    "causa_mas_recurrente",

                "informes":
                    "informes_causa_principal",

                "porcentaje_comunal":
                    "porcentaje_causa_principal"
            }
        )
    )

    panel = panel.merge(
        causa_principal,
        on="codigo_comuna",
        how="left",
        validate="one_to_one"
    )

    # ------------------------------------------------------
    # Integrar indicadores temporales
    # ------------------------------------------------------

    tiempos = duracion[
        [
            "codigo_comuna",
            "informes_validos",
            "mediana_horas",
            "percentil_75_horas"
        ]
    ].copy()

    panel = panel.merge(
        tiempos,
        on="codigo_comuna",
        how="left",
        validate="one_to_one"
    )

    # ------------------------------------------------------
    # Calcular cobertura temporal
    # ------------------------------------------------------

    panel["cobertura_temporal_pct"] = (
        panel["informes_validos"]
        .div(
            panel["asociaciones_documentales"].replace(
                0,
                float("nan")
            )
        )
        .mul(100)
        .round(2)
    )

    # ------------------------------------------------------
    # Validar integridad del panel
    # ------------------------------------------------------

    if panel["codigo_comuna"].duplicated().any():
        raise ValueError(
            "El panel contiene comunas duplicadas."
        )

    if len(panel) != len(frecuencia):
        raise ValueError(
            "La integración modificó la cantidad de comunas."
        )

    if panel["asociaciones_documentales"].sum() != len(
        asociaciones
    ):
        raise ValueError(
            "No se conservaron las asociaciones."
        )

    # ------------------------------------------------------
    # Ordenar el resultado
    # ------------------------------------------------------

    panel = (
        panel
        .sort_values(
            "frecuencia_100k_hab_anio",
            ascending=False
        )
        .reset_index(drop=True)
    )

    return panel
