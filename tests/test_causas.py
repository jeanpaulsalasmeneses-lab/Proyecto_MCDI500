"""
Pruebas de la tabla de equivalencias de causas (F4, decisión D-15).

Casos normales (corrige «Balckout»), límite (descripciones fuera de la
tabla, faltantes, serie vacía) y excepciones (tabla repetida, encadenada
o incompleta).

    python -m unittest discover tests -v
"""

import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.causas import (cargar_equivalencias_causas,  # noqa: E402
                        normalizar_descripcion_causa)


def escribir_tabla(texto):
    """Escribe una tabla de equivalencias temporal y devuelve su ruta."""

    archivo = tempfile.NamedTemporaryFile(
        "w", suffix=".csv", delete=False, encoding="utf-8"
    )
    archivo.write(texto)
    archivo.close()
    return archivo.name


class TestTablaVersionada(unittest.TestCase):
    """La tabla real de data/reference/ es válida y cubre los datos."""

    def test_tabla_del_repositorio_es_valida(self):
        tabla = cargar_equivalencias_causas()
        self.assertGreaterEqual(len(tabla), 1)
        self.assertIn("Balckout del sistema", set(tabla["descripcion_cen"]))

    def test_cada_correccion_existe_en_los_datos_de_f2(self):
        # Una fila que no corrige nada sería una regla muerta.
        datos = pd.read_csv(
            RAIZ / "data" / "processed" / "f2"
            / "04_cen_fallas_comunas_integrado.csv",
            usecols=["descripcion_causa"], low_memory=False
        )
        presentes = set(datos["descripcion_causa"].dropna())
        faltan = set(cargar_equivalencias_causas()["descripcion_cen"]) - presentes
        self.assertEqual(faltan, set())


class TestNormalizacion(unittest.TestCase):

    def setUp(self):
        self.tabla = cargar_equivalencias_causas()

    def test_corrige_balckout(self):
        serie = pd.Series(["Balckout del sistema"])
        resultado = normalizar_descripcion_causa(serie, self.tabla)
        self.assertEqual(resultado.iloc[0], "Blackout del sistema")

    def test_descripcion_fuera_de_la_tabla_no_cambia(self):
        serie = pd.Series(["Baja frecuencia", "Se investiga"])
        resultado = normalizar_descripcion_causa(serie, self.tabla)
        self.assertEqual(resultado.tolist(), ["Baja frecuencia", "Se investiga"])

    def test_faltantes_se_conservan(self):
        serie = pd.Series([None, "Balckout del sistema"], dtype="object")
        resultado = normalizar_descripcion_causa(serie, self.tabla)
        self.assertTrue(pd.isna(resultado.iloc[0]))
        self.assertEqual(resultado.iloc[1], "Blackout del sistema")

    def test_serie_vacia(self):
        resultado = normalizar_descripcion_causa(
            pd.Series([], dtype="object"), self.tabla
        )
        self.assertEqual(len(resultado), 0)

    def test_no_modifica_la_serie_original(self):
        serie = pd.Series(["Balckout del sistema"])
        normalizar_descripcion_causa(serie, self.tabla)
        self.assertEqual(serie.iloc[0], "Balckout del sistema")


class TestTablaInvalida(unittest.TestCase):

    CABECERA = "descripcion_cen,descripcion_normalizada,motivo\n"

    def test_descripcion_repetida(self):
        ruta = escribir_tabla(self.CABECERA + "A,B,x\nA,C,y\n")
        with self.assertRaises(ValueError):
            cargar_equivalencias_causas(ruta)

    def test_equivalencia_encadenada(self):
        ruta = escribir_tabla(self.CABECERA + "A,B,x\nB,C,y\n")
        with self.assertRaises(ValueError):
            cargar_equivalencias_causas(ruta)

    def test_columna_faltante(self):
        ruta = escribir_tabla("descripcion_cen,motivo\nA,x\n")
        with self.assertRaises(ValueError):
            cargar_equivalencias_causas(ruta)

    def test_celda_vacia(self):
        ruta = escribir_tabla(self.CABECERA + "A,,x\n")
        with self.assertRaises(ValueError):
            cargar_equivalencias_causas(ruta)


if __name__ == "__main__":
    unittest.main()
