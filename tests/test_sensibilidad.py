"""
Pruebas de la sensibilidad a Antofagasta (src/sensibilidad.py, issue #58).

Casos normales con valores conocidos, casos límite (informes sin
subestación, años sin informes, nueve meses en 2026) y excepciones
(consolidado con id repetido, año no declarado, comuna inexistente).

    python -m unittest discover tests -v
"""

import sys
import unittest
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.sensibilidad import (concentracion_por_comuna,  # noqa: E402
                              informes_por_anio, no_anulados,
                              resumen_con_y_sin, unir_instalaciones)


def asociaciones_de_prueba():
    """Seis vínculos: Alfa (4, uno anulado) y Beta (2)."""

    return pd.DataFrame({
        "id_falla": [1, 2, 3, 4, 5, 6],
        "codigo_comuna": ["01", "01", "01", "01", "02", "02"],
        "comuna_oficial": ["Alfa", "Alfa", "Alfa", "Alfa", "Beta", "Beta"],
        "estado_normalizado": ["FINALIZADO", "FINALIZADO", "ANULADO",
                               "FINALIZADO", "FINALIZADO", "PENDIENTE"],
        "fecha_perturbacion_dt": ["2024-01-10", "2025-03-01", "2025-04-01",
                                  "2026-02-01", "2024-05-05", "2026-08-08"],
        "fecha_termino_dt": ["2024-01-10 02:00", "2025-03-01 04:00", None,
                             "2026-02-01 01:00", "2024-05-05 03:00", None],
        "validacion_temporal": ["INTERVALO_NO_NEGATIVO"] * 2 + ["SIN_FECHA"]
                               + ["INTERVALO_NO_NEGATIVO"] * 2 + ["SIN_FECHA"],
        "intervalo_documental_horas": [2.0, 4.0, None, 1.0, 3.0, None],
        "descripcion_causa": ["Falla en equipo", "Falla en equipo", "Se investiga",
                              "Balckout del sistema", "Baja frecuencia", "Se investiga"],
    })


def panel_de_prueba():
    return pd.DataFrame({
        "comuna_oficial": ["Alfa", "Beta"],
        "poblacion_2024": [100_000, 300_000],
        "informes_no_anulados": [3, 2],
        "frecuencia_100k_hab_anio": [1.09, 0.24],
    })


class TestPreparacion(unittest.TestCase):

    def test_no_anulados_excluye_el_anulado(self):
        datos = no_anulados(asociaciones_de_prueba())
        self.assertEqual(sorted(datos["id_falla"]), [1, 2, 4, 5, 6])

    def test_unir_instalaciones_conserva_los_vinculos(self):
        eventos = pd.DataFrame({"id_falla": [1, 2, 3, 4, 5, 6],
                                "SubEstación": ["S1", "S1", "S1", None, "S9", "S9"],
                                "Empresa": ["E1"] * 4 + ["E2"] * 2})
        unidas = unir_instalaciones(asociaciones_de_prueba(), eventos)
        self.assertEqual(len(unidas), 6)
        self.assertEqual(unidas.loc[unidas["id_falla"] == 5, "Empresa"].item(), "E2")

    def test_consolidado_con_id_repetido(self):
        eventos = pd.DataFrame({"id_falla": [1, 1], "SubEstación": ["A", "B"],
                                "Empresa": ["E", "E"]})
        with self.assertRaises(ValueError):
            unir_instalaciones(asociaciones_de_prueba(), eventos)

    def test_consolidado_sin_columna(self):
        with self.assertRaises(ValueError):
            unir_instalaciones(asociaciones_de_prueba(), pd.DataFrame({"id_falla": [1]}))


class TestConcentracion(unittest.TestCase):

    def datos(self):
        return pd.DataFrame({
            "id_falla": [1, 2, 3, 4, 5, 6, 7],
            "comuna_oficial": ["Alfa"] * 5 + ["Beta"] * 2,
            "SubEstación": ["S1", "S1", "S1", "S2", None, "S8", "S9"],
        })

    def test_porcentajes_conocidos(self):
        r = concentracion_por_comuna(self.datos(), "SubEstación", top=1).set_index("comuna_oficial")
        # Alfa: 4 informes con dato, 3 en S1 -> 75 %; el informe sin dato no entra.
        self.assertEqual(r.loc["Alfa", "informes"], 5)
        self.assertEqual(r.loc["Alfa", "informes_con_dato"], 4)
        self.assertEqual(r.loc["Alfa", "principal"], "S1")
        self.assertEqual(r.loc["Alfa", "pct_principal"], 75.0)
        self.assertEqual(r.loc["Beta", "pct_top1"], 50.0)

    def test_top_mayor_que_los_distintos_da_100(self):
        r = concentracion_por_comuna(self.datos(), "SubEstación", top=5).set_index("comuna_oficial")
        self.assertEqual(r.loc["Alfa", "pct_top5"], 100.0)

    def test_top_invalido(self):
        with self.assertRaises(ValueError):
            concentracion_por_comuna(self.datos(), "SubEstación", top=0)


class TestPorAnio(unittest.TestCase):

    def test_anualizacion_y_ceros(self):
        datos = no_anulados(asociaciones_de_prueba())
        t = informes_por_anio(datos, panel_de_prueba()).set_index(["comuna_oficial", "anio"])
        # Alfa 2026: 1 informe, 100.000 hab., 9 meses -> 1 / 1 / 0,75 = 1,33.
        self.assertEqual(t.loc[("Alfa", 2026), "informes"], 1)
        self.assertEqual(t.loc[("Alfa", 2026), "frecuencia_100k_hab_anio"], 1.33)
        # Beta no tiene informes en 2025: la fila existe con cero.
        self.assertEqual(t.loc[("Beta", 2025), "informes"], 0)
        self.assertEqual(t.loc[("Alfa", 2024), "puesto"], 1)

    def test_anio_no_declarado(self):
        datos = asociaciones_de_prueba().assign(fecha_perturbacion_dt="2023-12-31")
        with self.assertRaises(ValueError):
            informes_por_anio(datos, panel_de_prueba())


class TestConYSin(unittest.TestCase):

    def test_resumen_con_y_sin(self):
        r = resumen_con_y_sin(asociaciones_de_prueba(), panel_de_prueba(), "Alfa",
                              meses_observados=12).set_index("indicador")
        self.assertEqual(r.loc["Comunas", "2 comunas"], 2)
        self.assertEqual(r.loc["Comunas", "sin Alfa"], 1)
        self.assertEqual(r.loc["Informes únicos no anulados", "2 comunas"], 5)
        # 5 vínculos / 400.000 hab. * 100.000 / 1 año = 1,25.
        self.assertEqual(r.loc["Frecuencia agregada (vínculos por 100.000 hab.-año)", "2 comunas"], 1.25)
        self.assertEqual(r.loc["Descripción causal determinada más frecuente", "2 comunas"],
                         "Falla en equipo")
        self.assertEqual(r.loc["Descripción causal determinada más frecuente", "sin Alfa"],
                         "Baja frecuencia")
        # Mediana de los intervalos elegibles: 1, 2, 3 y 4 -> 2,5; sin Alfa solo queda 3.
        self.assertEqual(r.loc["Mediana del intervalo documental (horas)", "2 comunas"], 2.5)
        self.assertEqual(r.loc["Mediana del intervalo documental (horas)", "sin Alfa"], 3.0)

    def test_comuna_inexistente(self):
        with self.assertRaises(ValueError):
            resumen_con_y_sin(asociaciones_de_prueba(), panel_de_prueba(), "Gamma")


if __name__ == "__main__":
    unittest.main()
