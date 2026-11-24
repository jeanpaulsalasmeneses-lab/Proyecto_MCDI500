"""
Pruebas de la comparación entre el script de consolidación y los archivos
versionados (src/verificar_consolidacion.py).

No necesitan los ZIP del CEN: comparan archivos pequeños creados en una
carpeta temporal. La comparación real se ejecuta con
python src/verificar_consolidacion.py.

    python -m unittest discover tests -v
"""

import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.verificar_consolidacion import (comparar_archivos,  # noqa: E402
                                         comparar_carpeta, sha256)


class TestComparacion(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.dir = Path(self.carpeta.name)

    def tearDown(self):
        self.carpeta.cleanup()

    def escribir(self, nombre, contenido):
        ruta = self.dir / nombre
        ruta.write_bytes(contenido)
        return ruta

    def test_archivos_identicos_coinciden(self):
        a = self.escribir("a.csv", b"id,valor\n1,2\n")
        b = self.escribir("b.csv", b"id,valor\n1,2\n")
        r = comparar_archivos(a, b)
        self.assertEqual(r["estado"], "COINCIDE")
        self.assertEqual(r["sha_versionado"], r["sha_generado"])

    def test_solo_cambia_el_fin_de_linea(self):
        # Caso límite: mismo contenido, CRLF frente a LF (los consolidados
        # versionados antes de D-04). No es byte a byte, pero sí equivalente.
        a = self.escribir("a.csv", b"id,valor\r\n1,2\r\n")
        b = self.escribir("b.csv", b"id,valor\n1,2\n")
        self.assertEqual(comparar_archivos(a, b)["estado"], "FIN_DE_LINEA")

    def test_contenido_distinto_difiere(self):
        a = self.escribir("a.csv", b"id,valor\r\n1,2\r\n")
        b = self.escribir("b.csv", b"id,valor\n1,3\n")
        self.assertEqual(comparar_archivos(a, b)["estado"], "DIFIERE")

    def test_archivo_faltante(self):
        a = self.escribir("a.csv", b"x\n")
        r = comparar_archivos(a, self.dir / "no_existe.csv")
        self.assertEqual(r["estado"], "FALTA")
        self.assertEqual(len(r["faltantes"]), 1)

    def test_sha256_conocido(self):
        # SHA-256 de la cadena vacía (valor de referencia).
        vacio = self.escribir("vacio.csv", b"")
        self.assertEqual(
            sha256(vacio),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )

    def test_comparar_carpeta(self):
        versionado = self.escribir("ref.csv", b"1\n")
        generados = self.dir / "generados"
        generados.mkdir()
        (generados / "salida.csv").write_bytes(b"1\n")
        r = comparar_carpeta(generados, {"salida.csv": versionado,
                                         "otra.csv": versionado})
        self.assertEqual(r["salida.csv"]["estado"], "COINCIDE")
        self.assertEqual(r["otra.csv"]["estado"], "FALTA")


if __name__ == "__main__":
    unittest.main()
