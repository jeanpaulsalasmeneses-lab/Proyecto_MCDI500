"""
Pruebas de los componentes de F4: incertidumbre y dimensión temporal.

Casos conocidos pedidos en la retroalimentación de F3: un conteo cero
da un intervalo con límite inferior cero, y una comuna con un solo
intervalo queda marcada como de baja precisión.

    python -m unittest discover tests -v
"""

import sys
import unittest
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.incertidumbre import (duracion_con_intervalo,  # noqa: E402
                               frecuencia_con_intervalo,
                               intervalo_bootstrap_mediana,
                               intervalo_poisson_exacto,
                               marcar_baja_precision,
                               pares_no_distinguibles, se_superponen)
from src.temporal import contar_informes_mensuales, peso_de_un_dia  # noqa: E402


def asociaciones_de_prueba():
    """Seis asociaciones de dos comunas, una anulada y dos del 25-02-2025."""

    return pd.DataFrame({
        "id_falla": ["A1", "A2", "A3", "A4", "B1", "B2"],
        "codigo_comuna": ["01", "01", "01", "01", "02", "02"],
        "comuna_oficial": ["Alfa", "Alfa", "Alfa", "Alfa", "Beta", "Beta"],
        "estado_normalizado": ["FINALIZADO", "PENDIENTE", "ANULADO",
                               "FINALIZADO", "FINALIZADO", "PENDIENTE"],
        "fecha_perturbacion_dt": ["2024-01-10 08:00", "2025-02-25 15:30",
                                  "2025-02-25 16:00", "2026-09-30 23:00",
                                  "2024-03-05 10:00", "2025-02-25 15:45"],
        "validacion_temporal": ["INTERVALO_NO_NEGATIVO", "SIN_FECHA_TERMINO",
                                "SIN_FECHA_TERMINO", "INTERVALO_NO_NEGATIVO",
                                "INTERVALO_NO_NEGATIVO", "SIN_FECHA_TERMINO"],
        "fecha_termino_dt": ["2024-01-10 10:00", None, None,
                             "2026-10-01 01:00", "2024-03-05 10:30", None],
        "intervalo_documental_horas": [2.0, None, None, 2.0, 0.5, None],
    })


class TestIntervaloPoisson(unittest.TestCase):

    def test_conteo_cero_tiene_limite_inferior_cero(self):
        inferior, superior = intervalo_poisson_exacto(0)
        self.assertEqual(inferior, 0.0)
        self.assertAlmostEqual(superior, 3.6889, places=3)

    def test_valores_de_referencia(self):
        # Valores publicados del intervalo exacto de Garwood al 95 %.
        inferior, superior = intervalo_poisson_exacto(10)
        self.assertAlmostEqual(inferior, 4.7954, places=3)
        self.assertAlmostEqual(superior, 18.3904, places=3)

    def test_el_intervalo_contiene_al_conteo(self):
        for conteo in (1, 35, 503):
            with self.subTest(conteo=conteo):
                inferior, superior = intervalo_poisson_exacto(conteo)
                self.assertLess(inferior, conteo)
                self.assertGreater(superior, conteo)

    def test_rechaza_conteo_negativo_o_decimal(self):
        with self.assertRaises(ValueError):
            intervalo_poisson_exacto(-1)
        with self.assertRaises(ValueError):
            intervalo_poisson_exacto(2.5)

    def test_frecuencia_reproduce_la_formula_de_f3(self):
        panel = pd.DataFrame({
            "codigo_comuna": ["01"],
            "comuna_oficial": ["Alfa"],
            "poblacion_2024": [100_000.0],
            "informes_no_anulados": [33],
        })
        tabla = frecuencia_con_intervalo(panel, meses_observados=33)
        # 33 informes / 100.000 hab. * 100.000 / 2,75 años = 12 por año.
        self.assertEqual(tabla.loc[0, "frecuencia_100k_hab_anio"], 12.0)
        self.assertLess(tabla.loc[0, "ic_inferior"], 12.0)
        self.assertGreater(tabla.loc[0, "ic_superior"], 12.0)


class TestBootstrapYPrecision(unittest.TestCase):

    def test_un_solo_intervalo_colapsa_y_es_baja_precision(self):
        inferior, superior = intervalo_bootstrap_mediana([4.0])
        self.assertEqual((inferior, superior), (4.0, 4.0))
        self.assertTrue(marcar_baja_precision(1))

    def test_sin_valores_devuelve_nan(self):
        inferior, superior = intervalo_bootstrap_mediana([])
        self.assertTrue(pd.isna(inferior) and pd.isna(superior))

    def test_semilla_fija_es_reproducible(self):
        valores = [0.3, 1.0, 1.5, 2.0, 2.2, 3.1, 6.0, 9.4]
        self.assertEqual(intervalo_bootstrap_mediana(valores),
                         intervalo_bootstrap_mediana(valores))

    def test_umbral_de_baja_precision(self):
        self.assertTrue(marcar_baja_precision(29))
        self.assertFalse(marcar_baja_precision(30))

    def test_duracion_usa_solo_intervalos_elegibles(self):
        tabla = duracion_con_intervalo(asociaciones_de_prueba())
        alfa = tabla.set_index("comuna_oficial").loc["Alfa"]
        self.assertEqual(alfa["intervalos_elegibles"], 2)
        self.assertEqual(alfa["mediana_horas"], 2.0)
        self.assertTrue(alfa["baja_precision"])


class TestComparacion(unittest.TestCase):

    def test_superposicion(self):
        self.assertTrue(se_superponen(1, 5, 4, 8))
        self.assertFalse(se_superponen(1, 3, 4, 8))

    def test_pares_no_distinguibles(self):
        tabla = pd.DataFrame({
            "comuna_oficial": ["A", "B", "C"],
            "ic_inferior": [40.0, 20.0, 18.0],
            "ic_superior": [50.0, 28.0, 23.0],
        })
        self.assertEqual(pares_no_distinguibles(tabla), [("B", "C")])


class TestTemporal(unittest.TestCase):

    def test_matriz_completa_y_sin_anulados(self):
        matriz = contar_informes_mensuales(asociaciones_de_prueba())
        self.assertEqual(matriz.shape, (2, 33))
        # A3 está anulado: Alfa tiene 3 informes, no 4.
        self.assertEqual(matriz.loc["Alfa"].sum(), 3)
        self.assertEqual(matriz.loc["Alfa", pd.Period("2025-02", "M")], 1)
        self.assertEqual(matriz.loc["Beta", pd.Period("2024-02", "M")], 0)

    def test_orden_de_comunas(self):
        matriz = contar_informes_mensuales(asociaciones_de_prueba(),
                                           orden_comunas=["Beta", "Alfa"])
        self.assertEqual(list(matriz.index), ["Beta", "Alfa"])

    def test_rechaza_informes_fuera_del_periodo(self):
        datos = asociaciones_de_prueba()
        datos.loc[0, "fecha_perturbacion_dt"] = "2023-12-31 10:00"
        with self.assertRaises(ValueError):
            contar_informes_mensuales(datos)

    def test_peso_del_apagon(self):
        tabla = peso_de_un_dia(asociaciones_de_prueba()).set_index(
            "comuna_oficial")
        self.assertEqual(tabla.loc["Alfa", "informes_del_dia"], 1)
        self.assertEqual(tabla.loc["Alfa", "informes_sin_dia"], 2)
        self.assertEqual(tabla.loc["Beta", "pct_del_dia"], 50.0)


if __name__ == "__main__":
    unittest.main()
