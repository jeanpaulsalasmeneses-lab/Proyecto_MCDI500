
from abc import ABC, abstractmethod
import pandas as pd

from .indicadores import (
    verificar_columnas,
    calcular_frecuencia_comunal,
    calcular_recurrencia_comunal,
    calcular_duracion_comunal
)


class FuenteDatos(ABC):
    """Clase abstracta de gestión de datos."""

    def __init__(self, datos):

        if not isinstance(datos, pd.DataFrame):
            raise TypeError("Se requiere un DataFrame.")

        self.__datos = datos.copy(deep=True)

    def obtener_datos(self):
        return self.__datos.copy(deep=True)

    @abstractmethod
    def validar(self):
        pass

    @abstractmethod
    def tipo_fuente(self):
        pass


class FuenteCEN(FuenteDatos):
    """Gestiona asociaciones documentales CEN."""

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
            raise ValueError("Identificadores CEN faltantes.")

        if datos.duplicated(
            ["id_falla", "codigo_comuna"]
        ).any():
            raise ValueError("Asociaciones CEN duplicadas.")

        return True

    def tipo_fuente(self):
        return "Coordinador Eléctrico Nacional"


class FuenteINE(FuenteDatos):
    """Gestiona datos territoriales INE."""

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
            raise ValueError("Códigos comunales faltantes.")

        if datos["codigo_comuna"].duplicated().any():
            raise ValueError("Comunas duplicadas.")

        if (
            poblacion.isna().any()
            or poblacion.le(0).any()
        ):
            raise ValueError("Población inválida.")

        return True

    def tipo_fuente(self):
        return "Instituto Nacional de Estadísticas"


class AnalizadorDuracion:
    """Analiza intervalos documentales elegibles."""

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
    """Integra los componentes analíticos."""

    def __init__(
        self,
        asociaciones,
        comunas,
        tiempos,
        meses_observados=33
    ):

        if meses_observados <= 0:
            raise ValueError("Periodo inválido.")

        self.__fuente_cen = FuenteCEN(asociaciones)

        self.__fuente_ine = FuenteINE(comunas)

        self.__analizador_duracion = AnalizadorDuracion(
            tiempos,
            comunas
        )

        self.__meses_observados = meses_observados

        self.validar_fuentes()

    def validar_fuentes(self):

        for fuente in [
            self.__fuente_cen,
            self.__fuente_ine
        ]:
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

        return {
            "frecuencia": self.analizar_frecuencia(),
            "recurrencia": self.analizar_recurrencia(),
            "duracion": self.analizar_duracion()
        }
