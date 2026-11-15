"""
Núcleo orientado a objetos de la Fase 3.

- FuenteDatos (abstracta) -> FuenteCEN y FuenteINE: herencia y polimorfismo
  (cada fuente implementa validar() y tipo_fuente()).
- AnalizadorDuracion y NucleoAnalitico: encapsulan los datos y coordinan los
  indicadores de src/indicadores.py.
"""

from abc import ABC, abstractmethod

import pandas as pd

from .indicadores import (
    calcular_duracion_comunal,
    calcular_frecuencia_comunal,
    calcular_recurrencia_comunal,
    verificar_columnas,
)


class FuenteDatos(ABC):
    """
    Clase base abstracta para gestionar conjuntos
    de datos previamente procesados.
    """

    def __init__(self, datos):

        if not isinstance(datos, pd.DataFrame):
            raise TypeError(
                "La fuente debe recibir un DataFrame."
            )

        # Encapsulamiento del conjunto de datos.

        self.__datos = datos.copy(deep=True)

    def obtener_datos(self):
        """
        Devuelve una copia para evitar
        modificaciones externas.
        """

        return self.__datos.copy(deep=True)

    @abstractmethod
    def validar(self):
        """
        Verifica la integridad de la fuente.
        """
        pass

    @abstractmethod
    def tipo_fuente(self):
        """
        Identifica el origen de los datos.
        """
        pass


class FuenteCEN(FuenteDatos):
    """
    Gestiona las asociaciones documentales
    provenientes del CEN.
    """

    def validar(self):

        datos = self.obtener_datos()

        verificar_columnas(
            datos,
            [
                "id_falla",
                "codigo_comuna",
                "estado_normalizado",
                "descripcion_causa"
            ],
            "FuenteCEN"
        )

        if datos[
            ["id_falla", "codigo_comuna"]
        ].isna().any().any():

            raise ValueError(
                "Existen identificadores CEN faltantes."
            )

        if datos.duplicated(
            ["id_falla", "codigo_comuna"]
        ).any():

            raise ValueError(
                "Existen asociaciones CEN duplicadas."
            )

        return True

    def tipo_fuente(self):
        return "Coordinador Eléctrico Nacional"


class FuenteINE(FuenteDatos):
    """
    Gestiona información territorial y
    población censada.
    """

    def validar(self):

        datos = self.obtener_datos()

        verificar_columnas(
            datos,
            [
                "codigo_comuna",
                "comuna_oficial",
                "poblacion_2024"
            ],
            "FuenteINE"
        )

        poblacion = pd.to_numeric(
            datos["poblacion_2024"],
            errors="coerce"
        )

        if datos["codigo_comuna"].isna().any():

            raise ValueError(
                "Existen códigos comunales faltantes."
            )

        if datos["codigo_comuna"].duplicated().any():

            raise ValueError(
                "Existen comunas duplicadas."
            )

        if poblacion.isna().any() or poblacion.le(0).any():

            raise ValueError(
                "La población censada no es válida."
            )

        return True

    def tipo_fuente(self):
        return "Instituto Nacional de Estadísticas"


class AnalizadorDuracion:
    """
    Gestiona el análisis de intervalos
    documentales de falla.

    Reutiliza la función estructurada
    previamente validada.
    """

    def __init__(self, tiempos, comunas):

        self.__tiempos = tiempos.copy(deep=True)

        self.__comunas = comunas.copy(deep=True)

    def calcular(self):

        return calcular_duracion_comunal(
            self.__tiempos,
            self.__comunas
        )

    def cantidad_intervalos_validos(self):

        datos = self.__tiempos

        return int(
            datos.loc[
                datos["intervalo_elegible"].fillna(False),
                "id_falla"
            ].nunique()
        )


class NucleoAnalitico:
    """
    Integra las fuentes de datos y los
    principales analizadores del proyecto.
    """

    def __init__(
        self,
        asociaciones,
        comunas,
        tiempos,
        meses_observados=33
    ):

        if meses_observados <= 0:
            raise ValueError(
                "El período debe ser positivo."
            )

        # Composición de las fuentes.

        self.__fuente_cen = FuenteCEN(
            asociaciones
        )

        self.__fuente_ine = FuenteINE(
            comunas
        )

        # Composición del analizador temporal.

        self.__analizador_duracion = AnalizadorDuracion(
            tiempos,
            comunas
        )

        self.__meses_observados = meses_observados

        self.validar_fuentes()

    def validar_fuentes(self):

        fuentes = [
            self.__fuente_cen,
            self.__fuente_ine
        ]

        for fuente in fuentes:

            fuente.validar()

        return True

    def analizar_frecuencia(self):

        return calcular_frecuencia_comunal(
            self.__fuente_cen.obtener_datos(),
            self.__fuente_ine.obtener_datos(),
            meses_observados=self.__meses_observados
        )

    def analizar_recurrencia(self, cantidad=3):

        return calcular_recurrencia_comunal(
            self.__fuente_cen.obtener_datos(),
            cantidad=cantidad
        )

    def analizar_duracion(self):

        return self.__analizador_duracion.calcular()

    def ejecutar(self):
        """
        Ejecuta las tres dimensiones analíticas.
        """

        return {
            "frecuencia": self.analizar_frecuencia(),
            "recurrencia": self.analizar_recurrencia(),
            "duracion": self.analizar_duracion()
        }
