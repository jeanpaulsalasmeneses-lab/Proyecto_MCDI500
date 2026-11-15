"""
Pruebas del script de consolidación (src/consolidar_fallas_2024_2026.py).

Usan ZIP pequeños construidos a mano, con resultados esperados conocidos:
casos normales, límite y excepciones. Ejecutar desde la raíz del proyecto:

    python -m unittest discover tests -v
"""

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import consolidar_fallas_2024_2026 as cf  # noqa: E402

ENCABEZADO = "Número,Estado,Comuna,Fecha Perturbación,Fecha Efectiva Fin\n"


def crear_zip(carpeta, nombre_zip, archivos):
    """Crea un ZIP con {nombre_interno: texto CSV} y devuelve su ruta."""
    ruta = Path(carpeta) / nombre_zip
    with zipfile.ZipFile(ruta, "w") as z:
        for nombre, texto in archivos.items():
            datos = texto if isinstance(texto, bytes) else texto.encode("utf-8-sig")
            z.writestr(nombre, datos)
    return ruta


class TestFuncionesIndividuales(unittest.TestCase):

    def test_periodo_desde_nombre_reconoce_solo_informes_de_fallas(self):
        self.assertEqual(cf.periodo_desde_nombre("x/2025_03_informe_fallas.csv"), (2025, 3))
        self.assertIsNone(cf.periodo_desde_nombre("2025_03_limitaciones.csv"))
        self.assertIsNone(cf.periodo_desde_nombre("2023_03_informe_fallas.csv"))  # fuera de 2024-2026
        self.assertIsNone(cf.periodo_desde_nombre("2025_13_informe_fallas.csv"))  # mes inválido

    def test_normalizar_id_falla_quita_decimal_y_vacios(self):
        numero = pd.Series([" 2024000001.0", "2024000002", "", None], dtype="string")
        resultado = cf.normalizar_id_falla(numero)
        self.assertEqual(resultado.iloc[0], "2024000001")
        self.assertEqual(resultado.iloc[1], "2024000002")
        self.assertTrue(pd.isna(resultado.iloc[2]))
        self.assertTrue(pd.isna(resultado.iloc[3]))

    def test_validar_estructura_limpia_espacios_en_columnas(self):
        df = pd.DataFrame(columns=[" Número ", "Fecha Perturbación", "Fecha Efectiva Fin "])
        self.assertIn("Número", cf.validar_estructura(df, "prueba.csv").columns)

    def test_validar_estructura_falla_si_falta_columna_esencial(self):
        df = pd.DataFrame(columns=["Número", "Fecha Perturbación"])
        with self.assertRaises(cf.ErrorConsolidacion):
            cf.validar_estructura(df, "prueba.csv")

    def test_agregar_trazabilidad_no_modifica_la_tabla_original(self):
        df = pd.DataFrame({"Número": ["1", "2"]})
        salida = cf.agregar_trazabilidad(df, 2024, 1, "a.zip", "b.csv")
        self.assertEqual(list(salida["fila_fuente"]), [2, 3])  # la fila 1 es el encabezado
        self.assertNotIn("fila_fuente", df.columns)


class TestConsolidacion(unittest.TestCase):

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.carpeta = Path(self.temporal.name)
        self.entrada = self.carpeta / "raw"
        self.entrada.mkdir()

    def tearDown(self):
        self.temporal.cleanup()

    def consolidar(self):
        return cf.consolidar(self.entrada, self.carpeta / "salida", self.carpeta / "docs",
                             informar=lambda _: None)

    def leer(self, nombre):
        return pd.read_csv(self.carpeta / "salida" / nombre, dtype=str, encoding="utf-8-sig")

    # --- Caso normal -------------------------------------------------------

    def test_caso_normal_dos_meses(self):
        crear_zip(self.entrada, "2024_01.zip", {"2024_01_informe_fallas.csv": ENCABEZADO
                  + "2024000001.0,finalizado,Arica,2024-01-01 10:00,2024-01-01 12:30\n"
                  + "2024000002,pendiente,Iquique,2024-01-02 08:00,\n",
                  "2024_01_limitaciones.csv": "otra,tabla\n1,2\n"})        # se ignora
        crear_zip(self.entrada, "2024_02.zip", {"2024_02_informe_fallas.csv": ENCABEZADO
                  + "2024000003,finalizado,Arica,2024-02-01 00:00,2024-02-01 01:00\n"})
        resumen = self.consolidar()

        self.assertEqual(resumen["publicados"], 3)
        self.assertEqual(resumen["eventos"], 3)
        self.assertEqual(resumen["duracion_valida"], 2)       # el pendiente no tiene fin
        eventos = self.leer("cen_fallas_2024_2026_eventos.csv")
        self.assertEqual(eventos.loc[0, "id_falla"], "2024000001")
        self.assertEqual(float(eventos.loc[0, "duracion_horas"]), 2.5)
        inventario = pd.read_csv(self.carpeta / "docs" / "inventario_fallas_2024_2026.csv")
        self.assertEqual(list(inventario["registros"]), [2, 1])
        self.assertEqual(list(inventario["columnas"]), [5, 5])  # columnas originales

    def test_salida_identica_en_cualquier_sistema(self):
        crear_zip(self.entrada, "2024_01.zip", {"2024_01_informe_fallas.csv": ENCABEZADO
                  + "1,finalizado,Arica,2024-01-01 10:00,2024-01-01 11:00\n"})
        self.consolidar()
        contenido = (self.carpeta / "salida" / "cen_fallas_2024_2026_eventos.csv").read_bytes()
        self.assertNotIn(b"\r\n", contenido)

    # --- Casos límite ------------------------------------------------------

    def test_limite_misma_falla_en_dos_meses_conserva_la_ultima_version(self):
        crear_zip(self.entrada, "2024_01.zip", {"2024_01_informe_fallas.csv": ENCABEZADO
                  + "77,pendiente,Arica,2024-01-01 10:00,\n"})
        crear_zip(self.entrada, "2024_02.zip", {"2024_02_informe_fallas.csv": ENCABEZADO
                  + "77,finalizado,Arica,2024-01-01 10:00,2024-01-01 11:00\n"})
        resumen = self.consolidar()
        self.assertEqual(resumen["publicados"], 2)
        self.assertEqual(resumen["repetidos"], 1)
        eventos = self.leer("cen_fallas_2024_2026_eventos.csv")
        self.assertEqual(len(eventos), 1)
        self.assertEqual(eventos.loc[0, "Estado"], "finalizado")
        self.assertEqual(eventos.loc[0, "mes_publicacion"], "2")

    def test_limite_sin_identificador_se_conserva_para_revision(self):
        crear_zip(self.entrada, "2024_01.zip", {"2024_01_informe_fallas.csv": ENCABEZADO
                  + ",finalizado,Arica,2024-01-01 10:00,2024-01-01 11:00\n"})
        resumen = self.consolidar()
        self.assertEqual(resumen["sin_identificador"], 1)
        self.assertEqual(resumen["eventos"], 1)

    def test_limite_intervalo_negativo_y_fecha_fuera_de_periodo(self):
        crear_zip(self.entrada, "2024_01.zip", {"2024_01_informe_fallas.csv": ENCABEZADO
                  + "1,finalizado,Arica,2024-01-01 10:00,2024-01-01 09:00\n"    # termina antes
                  + "2,finalizado,Arica,2018-05-01 10:00,2018-05-01 11:00\n"    # año 2018
                  + "3,finalizado,Arica,no-es-fecha,2024-01-01 11:00\n"})       # fecha inválida
        self.consolidar()
        eventos = self.leer("cen_fallas_2024_2026_eventos.csv").set_index("id_falla")
        self.assertEqual(eventos.loc["1", "intervalo_negativo"], "True")
        self.assertTrue(pd.isna(eventos.loc["1", "duracion_horas"]))   # no se usa como duración
        self.assertEqual(eventos.loc["2", "fuera_de_periodo"], "True")
        self.assertEqual(eventos.loc["3", "fecha_invalida_o_ausente"], "True")

    def test_limite_csv_en_latin1(self):
        texto = (ENCABEZADO + "1,finalizado,Peñalolén,2024-01-01 10:00,2024-01-01 11:00\n")
        crear_zip(self.entrada, "2024_01.zip", {"2024_01_informe_fallas.csv": texto.encode("latin-1")})
        self.consolidar()
        self.assertEqual(self.leer("cen_fallas_2024_2026_eventos.csv").loc[0, "Comuna"], "Peñalolén")

    # --- Excepciones -------------------------------------------------------

    def test_excepcion_mes_duplicado(self):
        fila = ENCABEZADO + "1,finalizado,Arica,2024-01-01 10:00,2024-01-01 11:00\n"
        crear_zip(self.entrada, "a.zip", {"2024_01_informe_fallas.csv": fila})
        crear_zip(self.entrada, "b.zip", {"2024_01_informe_fallas.csv": fila})
        with self.assertRaisesRegex(cf.ErrorConsolidacion, "duplicado"):
            self.consolidar()

    def test_excepcion_columna_esencial_faltante(self):
        crear_zip(self.entrada, "2024_01.zip", {"2024_01_informe_fallas.csv":
                  "Número,Estado\n1,finalizado\n"})
        with self.assertRaisesRegex(cf.ErrorConsolidacion, "faltan columnas"):
            self.consolidar()

    def test_excepcion_zip_danado(self):
        (self.entrada / "2024_01.zip").write_bytes(b"esto no es un zip")
        with self.assertRaisesRegex(cf.ErrorConsolidacion, "dañado"):
            self.consolidar()

    def test_excepcion_carpeta_sin_informes(self):
        with self.assertRaisesRegex(cf.ErrorConsolidacion, "No se encontraron"):
            self.consolidar()


if __name__ == "__main__":
    unittest.main()
