"""
Componentes que aprenden de los datos (Fase 3).

Guía de la Sumativa 2, paso 2: «una clase tiene sentido cuando el componente
necesita recordar algo entre una llamada y otra». Aquí, dos pasos del
pipeline aprenden de una tabla de referencia y después aplican lo aprendido:

- HomologadorComunal       aprende el maestro de comunas del INE y las
                           equivalencias, y asigna el código oficial a cada vínculo.
- NormalizadorPoblacional  aprende la población de cada comuna y convierte
                           conteos en tasas por 100.000 habitantes-año.

Patrón de diseño: Template Method. Transformador fija el algoritmo común
(validar -> aprender -> marcar como ajustado; exigir ajuste -> copiar ->
aplicar) y cada subclase implementa solo los pasos que cambian, _aprender y
_aplicar. El problema que resuelve: las validaciones y la protección de los
datos originales (siempre se trabaja sobre una copia) se escriben una sola
vez y ningún paso puede saltárselas.

Principios de POO:
- Encapsulamiento: lo aprendido se guarda en self._parametros y solo se
  expone como copia de lectura (propiedad parametros).
- Herencia: los dos componentes heredan ajustar/transformar de Transformador.
- Polimorfismo: el Pipeline (src/pipeline.py) llama a transformar() de cada
  paso sin preguntar su tipo.
"""

from abc import ABC, abstractmethod

import pandas as pd


class Transformador(ABC):
    """Clase base: ajustar() aprende de una referencia y transformar() aplica."""

    #: Columnas que debe traer la tabla de referencia de ajustar().
    columnas_ajuste = ()
    #: Columnas que debe traer la tabla de transformar().
    columnas_entrada = ()

    def __init__(self):
        self._parametros = {}
        self._ajustado = False

    @property
    def nombre(self):
        return type(self).__name__

    @property
    def ajustado(self):
        return self._ajustado

    @property
    def parametros(self):
        """Copia de lo aprendido: modificarla no altera el componente."""
        return dict(self._parametros)

    @staticmethod
    def _exigir_columnas(datos, columnas, contexto):
        if not isinstance(datos, pd.DataFrame):
            raise TypeError(f"{contexto}: se esperaba un DataFrame y llegó {type(datos).__name__}.")
        faltan = set(columnas) - set(datos.columns)
        if faltan:
            raise ValueError(f"{contexto}: faltan columnas {sorted(faltan)}.")

    def ajustar(self, referencia):
        """Template Method: valida, aprende y marca el componente como ajustado."""
        self._exigir_columnas(referencia, self.columnas_ajuste, f"{self.nombre}.ajustar")
        self._parametros = self._aprender(referencia.copy())
        self._ajustado = True
        return self

    def transformar(self, datos):
        """Template Method: exige ajuste previo y aplica sobre una copia."""
        if not self._ajustado:
            raise RuntimeError(f"{self.nombre}: llame a ajustar() antes de transformar().")
        self._exigir_columnas(datos, self.columnas_entrada, f"{self.nombre}.transformar")
        return self._aplicar(datos.copy())

    def ajustar_transformar(self, referencia, datos):
        return self.ajustar(referencia).transformar(datos)

    @abstractmethod
    def _aprender(self, referencia):
        """Devuelve un diccionario con lo aprendido de la referencia."""

    @abstractmethod
    def _aplicar(self, datos):
        """Transforma la copia de los datos con lo aprendido."""

    def __repr__(self):
        estado = "ajustado" if self._ajustado else "sin ajustar"
        return f"{self.nombre}({estado})"


class HomologadorComunal(Transformador):
    """
    Asigna el código comunal oficial del INE a cada vínculo informe–comuna.

    Aprende del maestro del INE la correspondencia clave -> comuna oficial.
    Primero aplica las equivalencias de data/reference/ (por ejemplo, LLAY
    LLAY -> LLAILLAY) y después busca la clave en el maestro.
    """

    columnas_ajuste = ("codigo_comuna", "comuna_oficial", "comuna_clave", "region_oficial",
                       "poblacion_2024")
    columnas_entrada = ("comuna_clave",)

    def __init__(self, equivalencias):
        super().__init__()
        self._equivalencias = dict(zip(equivalencias["clave_cen"], equivalencias["clave_ine"]))

    def _aprender(self, referencia):
        if referencia["comuna_clave"].duplicated().any():
            raise ValueError("El maestro del INE tiene claves de comuna repetidas.")
        maestro = referencia.set_index("comuna_clave")
        destinos_inexistentes = set(self._equivalencias.values()) - set(maestro.index)
        if destinos_inexistentes:
            raise ValueError(f"Equivalencias hacia comunas que no están en el INE: "
                             f"{sorted(destinos_inexistentes)}")
        return {
            "maestro": maestro[["codigo_comuna", "comuna_oficial", "region_oficial",
                                "poblacion_2024"]].to_dict("index"),
            "equivalencias": dict(self._equivalencias),
        }

    def _aplicar(self, datos):
        maestro = self._parametros["maestro"]
        equivalencias = self._parametros["equivalencias"]
        clave_ine = datos["comuna_clave"].map(lambda clave: equivalencias.get(clave, clave))
        for columna in ("codigo_comuna", "comuna_oficial", "region_oficial", "poblacion_2024"):
            datos[columna] = clave_ine.map(lambda clave: maestro.get(clave, {}).get(columna))
        datos["metodo_homologacion"] = "SIN_CORRESPONDENCIA"
        datos.loc[datos["codigo_comuna"].notna(), "metodo_homologacion"] = "EQUIVALENCIA"
        datos.loc[datos["comuna_clave"].isin(maestro.keys()), "metodo_homologacion"] = "COINCIDENCIA_EXACTA"
        return datos


class NormalizadorPoblacional(Transformador):
    """
    Convierte un conteo por comuna en tasa por 100.000 habitantes-año (D-06).

    Aprende la población de cada comuna. La tasa es
    conteo / (población / 100.000) / (meses observados / 12).
    La población es un denominador territorial: no representa clientes.
    """

    columnas_ajuste = ("codigo_comuna", "poblacion_2024")
    columnas_entrada = ("codigo_comuna",)

    def __init__(self, columna_conteo="informes_no_anulados", meses_observados=33, por=100_000,
                 columna_tasa="tasa_100k_hab_anio"):
        super().__init__()
        if meses_observados <= 0:
            raise ValueError("El período observado debe ser positivo.")
        self.columna_conteo = columna_conteo
        self.columna_tasa = columna_tasa
        self._anios = meses_observados / 12
        self._por = por

    def _aprender(self, referencia):
        poblacion = pd.to_numeric(referencia["poblacion_2024"], errors="coerce")
        if referencia["codigo_comuna"].duplicated().any():
            raise ValueError("Hay códigos de comuna repetidos en la referencia.")
        if poblacion.isna().any() or poblacion.le(0).any():
            raise ValueError("La población debe ser un número positivo en todas las comunas.")
        return {"poblacion": dict(zip(referencia["codigo_comuna"], poblacion)),
                "anios_observados": self._anios, "por": self._por}

    def _aplicar(self, datos):
        self._exigir_columnas(datos, (self.columna_conteo,), f"{self.nombre}.transformar")
        poblacion = datos["codigo_comuna"].map(self._parametros["poblacion"])
        if poblacion.isna().any():
            sin_poblacion = sorted(datos.loc[poblacion.isna(), "codigo_comuna"].unique())
            raise ValueError(f"Comunas sin población aprendida: {sin_poblacion}")
        datos[self.columna_tasa] = (
            datos[self.columna_conteo] / (poblacion / self._parametros["por"])
            / self._parametros["anios_observados"]
        )
        return datos
