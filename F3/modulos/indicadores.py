
import pandas as pd


def verificar_columnas(df, columnas, nombre):
    """Verifica las columnas requeridas."""

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
    """Calcula frecuencia documental normalizada."""

    if meses_observados <= 0:
        raise ValueError("Periodo de referencia inválido.")

    verificar_columnas(
        asociaciones,
        ["id_falla", "codigo_comuna", "estado_normalizado"],
        "asociaciones"
    )

    verificar_columnas(
        comunas,
        ["codigo_comuna", "comuna_oficial", "poblacion_2024"],
        "comunas"
    )

    datos = asociaciones[
        ["id_falla", "codigo_comuna", "estado_normalizado"]
    ].copy()

    if datos.duplicated(
        ["id_falla", "codigo_comuna"]
    ).any():
        raise ValueError("Asociaciones duplicadas.")

    datos["estado_normalizado"] = (
        datos["estado_normalizado"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    if datos["estado_normalizado"].isna().any():
        raise ValueError("Existen estados faltantes.")

    datos = datos.loc[
        datos["estado_normalizado"].ne("ANULADO")
    ].copy()

    conteos = (
        datos.groupby("codigo_comuna", as_index=False)
        .agg(
            informes_no_anulados=("id_falla", "nunique")
        )
    )

    maestro = comunas[
        ["codigo_comuna", "comuna_oficial", "poblacion_2024"]
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
        raise ValueError("Maestro comunal inválido.")

    if not datos["codigo_comuna"].isin(
        maestro["codigo_comuna"]
    ).all():
        raise ValueError("Códigos comunales no reconocidos.")

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

    resultado["frecuencia_100k_hab_anio"] = (
        resultado["informes_no_anulados"]
        / resultado["poblacion_2024"]
        * 100000
        / (meses_observados / 12)
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
    """Identifica descripciones causales recurrentes."""

    if cantidad < 1:
        raise ValueError("Cantidad inválida.")

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
        raise ValueError("Asociaciones duplicadas.")

    datos["descripcion_causa"] = (
        datos["descripcion_causa"]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    categorias_excluidas = {
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

    clave = (
        datos["descripcion_causa"]
        .str.upper()
        .str.rstrip(".")
    )

    datos_validos = datos.loc[
        clave.notna()
        & ~clave.isin(categorias_excluidas)
    ].copy()

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

    totales = (
        datos.groupby("codigo_comuna", as_index=False)
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

    recurrencias = recurrencias.sort_values(
        [
            "comuna_oficial",
            "informes",
            "descripcion_causa"
        ],
        ascending=[True, False, True]
    )

    return (
        recurrencias
        .groupby("codigo_comuna", group_keys=False)
        .head(cantidad)
        .reset_index(drop=True)
    )


def calcular_duracion_comunal(tiempos, comunas):
    """Calcula estadísticas de intervalos documentales."""

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
        ["codigo_comuna", "comuna_oficial"],
        "comunas"
    )

    datos = tiempos.copy()

    if datos.duplicated(
        ["id_falla", "codigo_comuna"]
    ).any():
        raise ValueError("Asociaciones temporales duplicadas.")

    datos["intervalo_horas"] = pd.to_numeric(
        datos["intervalo_horas"],
        errors="coerce"
    )

    validos = datos.loc[
        datos["intervalo_elegible"].fillna(False)
    ].copy()

    if (
        validos["intervalo_horas"].isna().any()
        or validos["intervalo_horas"].lt(0).any()
    ):
        raise ValueError("Intervalos elegibles inválidos.")

    resumen = (
        validos
        .groupby("codigo_comuna", as_index=False)
        .agg(
            informes_validos=("id_falla", "nunique"),
            mediana_horas=("intervalo_horas", "median"),
            percentil_75_horas=(
                "intervalo_horas",
                lambda x: x.quantile(0.75)
            )
        )
    )

    resultado = comunas[
        ["codigo_comuna", "comuna_oficial"]
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
    """Integra los indicadores en un panel comunal."""

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
        ["id_falla", "codigo_comuna"],
        "asociaciones"
    )

    if (
        frecuencia["codigo_comuna"].duplicated().any()
        or duracion["codigo_comuna"].duplicated().any()
    ):
        raise ValueError("Comunas duplicadas.")

    if asociaciones.duplicated(
        ["id_falla", "codigo_comuna"]
    ).any():
        raise ValueError("Asociaciones duplicadas.")

    panel = frecuencia[
        [
            "codigo_comuna",
            "comuna_oficial",
            "poblacion_2024",
            "informes_no_anulados",
            "frecuencia_100k_hab_anio"
        ]
    ].copy()

    totales = (
        asociaciones
        .groupby("codigo_comuna", as_index=False)
        .agg(
            asociaciones_documentales=("id_falla", "size")
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

    causas = (
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
                "descripcion_causa": "causa_mas_recurrente",
                "informes": "informes_causa_principal",
                "porcentaje_comunal": "porcentaje_causa_principal"
            }
        )
    )

    panel = panel.merge(
        causas,
        on="codigo_comuna",
        how="left",
        validate="one_to_one"
    )

    panel = panel.merge(
        duracion[
            [
                "codigo_comuna",
                "informes_validos",
                "mediana_horas",
                "percentil_75_horas"
            ]
        ],
        on="codigo_comuna",
        how="left",
        validate="one_to_one"
    )

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

    if (
        panel["codigo_comuna"].duplicated().any()
        or len(panel) != len(frecuencia)
    ):
        raise ValueError("Integración territorial inválida.")

    if (
        panel["asociaciones_documentales"].sum()
        != len(asociaciones)
    ):
        raise ValueError("No se conservaron las asociaciones.")

    return (
        panel
        .sort_values(
            "frecuencia_100k_hab_anio",
            ascending=False
        )
        .reset_index(drop=True)
    )
