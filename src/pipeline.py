"""
Pipeline de la Fase 3: encadena funciones y transformadores en un flujo único.

Guía de la Sumativa 2, paso 3: «un componente que reciba la lista ordenada
de pasos y los aplique uno tras otro», ejecutable con una sola llamada.

- Pipeline aplica cada paso con la misma llamada (polimorfismo): si el paso
  es un Transformador ya ajustado, usa transformar(); si es una función sin
  estado, la llama. No pregunta de qué clase es cada paso.
- Cada ejecución queda en una bitácora (paso, filas de entrada y de salida).
- ejecutar() reconstruye, desde los datos originales, los vínculos
  informe–comuna homologados de F2, y tasa_por_comuna() calcula el
  indicador de exposición de F3.
"""

import pandas as pd

from .territorio import limpiar_texto, separar_vinculos_vectorizado
from .transformadores import HomologadorComunal, NormalizadorPoblacional


class Pipeline:
    """Lista ordenada de pasos (nombre, paso) que se aplican en secuencia."""

    def __init__(self, pasos):
        self.pasos = list(pasos)
        self.bitacora = []

    def transformar(self, datos):
        self.bitacora = []
        for nombre, paso in self.pasos:
            filas_entrada = len(datos)
            # Polimorfismo: todos los pasos se aplican igual, sin consultar su tipo.
            datos = paso.transformar(datos) if hasattr(paso, "transformar") else paso(datos)
            self.bitacora.append({"paso": nombre, "filas_entrada": filas_entrada,
                                  "filas_salida": len(datos)})
        return datos

    def resumen(self):
        return pd.DataFrame(self.bitacora)

    def __len__(self):
        return len(self.pasos)

    def __repr__(self):
        return "Pipeline(" + " -> ".join(nombre for nombre, _ in self.pasos) + ")"


def agregar_estado(eventos):
    """Función que devuelve otra función: agrega el estado normalizado a los vínculos."""
    estados = eventos.drop_duplicates("id_falla").set_index("id_falla")["Estado"]
    estados = estados.map(limpiar_texto).str.upper()

    def paso(vinculos):
        salida = vinculos.copy()
        salida["estado_normalizado"] = salida["id_falla"].map(estados)
        return salida

    return paso


def ejecutar(eventos, maestro_ine, equivalencias):
    """
    Vínculos informe–comuna homologados con el INE, en una sola llamada.

    eventos:       data/processed/cen_fallas_2024_2026_eventos.csv
    maestro_ine:   territorio.cargar_maestro_ine(data/external/...)
    equivalencias: data/reference/equivalencias_comunas.csv
    Devuelve (vínculos, pipeline). El pipeline conserva su bitácora.
    """
    homologador = HomologadorComunal(equivalencias).ajustar(maestro_ine)
    pipeline = Pipeline([
        ("separar_vinculos", lambda _: separar_vinculos_vectorizado(eventos)),
        ("homologar_ine", homologador),
        ("agregar_estado", agregar_estado(eventos)),
    ])
    return pipeline.transformar(eventos), pipeline


def contar_informes_no_anulados(vinculos):
    """Informes distintos no anulados por comuna (los anulados se excluyen, D-05)."""
    validos = vinculos.loc[vinculos["estado_normalizado"].ne("ANULADO")]
    return (validos.groupby("codigo_comuna", as_index=False)
            .agg(informes_no_anulados=("id_falla", "nunique")))


def tasa_por_comuna(vinculos, comunas, meses_observados=33):
    """Tasa de exposición por 100.000 habitantes-año para las comunas indicadas."""
    normalizador = NormalizadorPoblacional(meses_observados=meses_observados).ajustar(comunas)
    seleccion = vinculos.loc[vinculos["codigo_comuna"].isin(comunas["codigo_comuna"])]
    pipeline = Pipeline([
        ("contar_no_anulados", contar_informes_no_anulados),
        ("normalizar_poblacion", normalizador),
    ])
    return pipeline.transformar(seleccion), pipeline
