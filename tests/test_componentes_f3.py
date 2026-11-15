"""
Pruebas de los componentes de la Fase 3 en src/.

Tablas pequeñas construidas a mano, con resultado esperado conocido:
casos normales, límite y excepciones (guía de la Sumativa 2, paso 6).

    python -m unittest discover tests -v
"""

import sys
import unittest
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.indicadores import verificar_columnas  # noqa: E402
from src.pipeline import Pipeline, contar_informes_no_anulados  # noqa: E402
from src.recorridos import (construir_jerarquia, sumar_asociaciones_iterativo,  # noqa: E402
                            sumar_asociaciones_recursivo)
from src.territorio import (normalizar_comuna, separar_vinculos_bucle,  # noqa: E402
                            separar_vinculos_vectorizado)
from src.transformadores import (HomologadorComunal, NormalizadorPoblacional,  # noqa: E402
                                 Transformador)

MAESTRO = pd.DataFrame({
    "codigo_comuna": ["05703", "15101", "13201"],
    "comuna_oficial": ["Llaillay", "Arica", "Puente Alto"],
    "comuna_clave": ["LLAILLAY", "ARICA", "PUENTE ALTO"],
    "region_oficial": ["Valparaíso", "Arica y Parinacota", "Metropolitana de Santiago"],
    "poblacion_2024": [25000.0, 241653.0, 568086.0],
})
EQUIVALENCIAS = pd.DataFrame({"clave_cen": ["LLAY LLAY"], "clave_ine": ["LLAILLAY"]})


class TestTerritorio(unittest.TestCase):

    def test_normalizar_comuna(self):
        self.assertEqual(normalizar_comuna("  Viña   del Mar "), "VINA DEL MAR")
        self.assertEqual(normalizar_comuna("Peñalolén"), "PENALOLEN")
        self.assertTrue(pd.isna(normalizar_comuna("   ")))
        self.assertTrue(pd.isna(normalizar_comuna(None)))

    def test_separar_vinculos_bucle_y_vectorizado_coinciden(self):
        eventos = pd.DataFrame({
            "id_falla": ["1", "2", "3", "4"],
            "Comuna": ["Arica | Iquique", "Arica||  Arica ", None, " Viña del Mar "],
            "Zona Afectada": ["Arica y Parinacota | Tarapacá", "Arica", "Biobío", "Valparaíso"],
        })
        bucle = separar_vinculos_bucle(eventos)
        vectorizado = separar_vinculos_vectorizado(eventos)
        self.assertTrue(bucle.astype(object).equals(vectorizado.astype(object)))
        # «A | B» genera 2 vínculos; «Arica||Arica» genera 1 (vacíos y repetidos fuera);
        # el informe sin comuna no genera vínculos.
        self.assertEqual(list(vectorizado["id_falla"]), ["1", "1", "2", "4"])
        self.assertEqual(vectorizado.loc[3, "comuna_clave"], "VINA DEL MAR")


class TestTransformadorBase(unittest.TestCase):

    def test_no_se_puede_instanciar_la_clase_abstracta(self):
        with self.assertRaises(TypeError):
            Transformador()

    def test_transformar_antes_de_ajustar_es_un_error(self):
        with self.assertRaisesRegex(RuntimeError, "ajustar"):
            HomologadorComunal(EQUIVALENCIAS).transformar(pd.DataFrame({"comuna_clave": ["ARICA"]}))

    def test_encapsulamiento_parametros_es_una_copia(self):
        homologador = HomologadorComunal(EQUIVALENCIAS).ajustar(MAESTRO)
        copia = homologador.parametros
        copia["maestro"] = {}
        self.assertEqual(len(homologador.parametros["maestro"]), 3)

    def test_ajustar_exige_dataframe_y_columnas(self):
        with self.assertRaises(TypeError):
            HomologadorComunal(EQUIVALENCIAS).ajustar([1, 2, 3])
        with self.assertRaisesRegex(ValueError, "faltan columnas"):
            HomologadorComunal(EQUIVALENCIAS).ajustar(MAESTRO.drop(columns="region_oficial"))


class TestHomologadorComunal(unittest.TestCase):

    def setUp(self):
        self.homologador = HomologadorComunal(EQUIVALENCIAS).ajustar(MAESTRO)

    def test_normal_coincidencia_exacta_y_equivalencia(self):
        vinculos = pd.DataFrame({"comuna_clave": ["ARICA", "LLAY LLAY"]})
        salida = self.homologador.transformar(vinculos)
        self.assertEqual(list(salida["codigo_comuna"]), ["15101", "05703"])
        self.assertEqual(list(salida["metodo_homologacion"]), ["COINCIDENCIA_EXACTA", "EQUIVALENCIA"])
        self.assertNotIn("codigo_comuna", vinculos.columns)   # no modifica la entrada

    def test_limite_comuna_sin_correspondencia(self):
        salida = self.homologador.transformar(pd.DataFrame({"comuna_clave": ["COMUNA INVENTADA"]}))
        self.assertTrue(pd.isna(salida.loc[0, "codigo_comuna"]))
        self.assertEqual(salida.loc[0, "metodo_homologacion"], "SIN_CORRESPONDENCIA")

    def test_excepcion_equivalencia_hacia_comuna_inexistente(self):
        malas = pd.DataFrame({"clave_cen": ["X"], "clave_ine": ["NO EXISTE"]})
        with self.assertRaisesRegex(ValueError, "no están en el INE"):
            HomologadorComunal(malas).ajustar(MAESTRO)

    def test_excepcion_maestro_con_claves_repetidas(self):
        repetido = pd.concat([MAESTRO, MAESTRO.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "repetidas"):
            HomologadorComunal(EQUIVALENCIAS).ajustar(repetido)


class TestNormalizadorPoblacional(unittest.TestCase):

    def test_normal_tasa_por_100k_habitantes_anio(self):
        # 11 informes, 100.000 habitantes, 33 meses (2,75 años) -> 11 / 1 / 2,75 = 4,0
        referencia = pd.DataFrame({"codigo_comuna": ["A"], "poblacion_2024": [100000]})
        conteos = pd.DataFrame({"codigo_comuna": ["A"], "informes_no_anulados": [11]})
        salida = NormalizadorPoblacional().ajustar(referencia).transformar(conteos)
        self.assertAlmostEqual(salida.loc[0, "tasa_100k_hab_anio"], 4.0)

    def test_limite_conteo_cero(self):
        referencia = pd.DataFrame({"codigo_comuna": ["A"], "poblacion_2024": [5000]})
        conteos = pd.DataFrame({"codigo_comuna": ["A"], "informes_no_anulados": [0]})
        salida = NormalizadorPoblacional().ajustar(referencia).transformar(conteos)
        self.assertEqual(salida.loc[0, "tasa_100k_hab_anio"], 0)

    def test_excepcion_poblacion_no_positiva(self):
        for poblacion in (0, -10, None):
            with self.subTest(poblacion=poblacion), self.assertRaisesRegex(ValueError, "positivo"):
                NormalizadorPoblacional().ajustar(
                    pd.DataFrame({"codigo_comuna": ["A"], "poblacion_2024": [poblacion]}))

    def test_excepcion_comuna_sin_poblacion_aprendida(self):
        normalizador = NormalizadorPoblacional().ajustar(
            pd.DataFrame({"codigo_comuna": ["A"], "poblacion_2024": [1000]}))
        with self.assertRaisesRegex(ValueError, "sin población"):
            normalizador.transformar(pd.DataFrame({"codigo_comuna": ["B"], "informes_no_anulados": [1]}))

    def test_excepcion_periodo_no_positivo(self):
        with self.assertRaises(ValueError):
            NormalizadorPoblacional(meses_observados=0)


class TestPipeline(unittest.TestCase):

    def test_polimorfismo_funciones_y_transformadores_con_la_misma_llamada(self):
        vinculos = pd.DataFrame({
            "id_falla": ["1", "2", "3", "3"],
            "codigo_comuna": ["A", "A", "A", "B"],
            "estado_normalizado": ["FINALIZADO", "ANULADO", "PENDIENTE", "PENDIENTE"],
        })
        referencia = pd.DataFrame({"codigo_comuna": ["A", "B"], "poblacion_2024": [100000, 50000]})
        pipeline = Pipeline([
            ("contar", contar_informes_no_anulados),                          # función
            ("normalizar", NormalizadorPoblacional().ajustar(referencia)),    # transformador
        ])
        salida = pipeline.transformar(vinculos).set_index("codigo_comuna")
        self.assertEqual(salida.loc["A", "informes_no_anulados"], 2)          # el anulado no cuenta
        self.assertEqual(len(pipeline), 2)
        self.assertEqual(list(pipeline.resumen()["paso"]), ["contar", "normalizar"])
        self.assertEqual(repr(pipeline), "Pipeline(contar -> normalizar)")


class TestFuncionesDeJeanEnSrc(unittest.TestCase):
    """Funciones del núcleo de F3 que pasaron del notebook a src/."""

    def setUp(self):
        self.tabla = pd.DataFrame({
            "region_oficial": ["R1", "R1", "R2"],
            "codigo_comuna": ["C1", "C2", "C3"],
            "tipo_instalacion": ["Línea", "Subestación", "Línea"],
            "asociaciones": [3, 4, 5],
        })

    def test_recursivo_e_iterativo_dan_el_mismo_total(self):
        arbol = construir_jerarquia(self.tabla)
        self.assertEqual(sumar_asociaciones_recursivo(arbol), 12)
        self.assertEqual(sumar_asociaciones_iterativo(arbol), 12)

    def test_limite_jerarquia_vacia(self):
        self.assertEqual(sumar_asociaciones_recursivo({}), 0)
        self.assertEqual(sumar_asociaciones_iterativo({}), 0)

    def test_excepcion_valor_negativo_o_nodo_invalido(self):
        with self.assertRaises(ValueError):
            sumar_asociaciones_recursivo({"R": {"C": {"Línea": -1}}})
        with self.assertRaises(TypeError):
            sumar_asociaciones_recursivo({"R": "no es un nodo"})

    def test_verificar_columnas(self):
        verificar_columnas(self.tabla, ["codigo_comuna"], "tabla")
        with self.assertRaises(ValueError):
            verificar_columnas(self.tabla, ["no_existe"], "tabla")


if __name__ == "__main__":
    unittest.main()
