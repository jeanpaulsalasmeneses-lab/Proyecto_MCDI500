"""
Genera el informe final de la Sumativa 3 (Fase 4, PDF) desde informe_sumativa3.md.

Uso, desde la raíz del proyecto y con el .venv activo:

    python -m pip install -r docs/entregas/sumativa1/requirements-informe.txt
    python docs/entregas/sumativa3/generar_informe.py

- El texto se edita SOLO en informe_sumativa3.md. Este script le da formato:
  portada, índice automático (apartados 2 a 29 con su jerarquía), tamaño carta,
  Arial 11 pt y numeración de páginas.
- Los datos del repositorio ({{COMMIT}}, {{TABLA_COMMITS}}, {{REPO}}) se
  calculan con Git al generar el PDF.
- Las figuras van dentro del texto, al ancho de la página, con su pie debajo.
- Verifica con assert que ningún texto quede bajo 11 pt, que ningún bloque se
  salga del margen y que el PDF no supere las 10 páginas que pide la guía.

Salida: docs/entregas/sumativa3/f4_s04_grupo7.pdf. Es un BORRADOR sin la
plantilla institucional: el contenido se traslada a esa plantilla antes de entregar.
"""

import re
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily, stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable, Frame, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Preformatted, Spacer, Table,
                                TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
FUENTE_MD = AQUI / "informe_sumativa3.md"
LOGO = RAIZ / "docs" / "entregas" / "sumativa1" / "logo_unab.png"
SALIDA = AQUI / "f4_s04_grupo7.pdf"
MAX_PAGINAS = 10
REPO = "https://github.com/jeanpaulsalasmeneses-lab/Proyecto_MCDI500"

LETRA = 11                      # tamaño mínimo y general del documento
MARGEN = 2.0 * cm
ANCHO_UTIL = letter[0] - 2 * MARGEN

AZUL, ROJO, GRIS = colors.HexColor("#141D2E"), colors.HexColor("#AE1F2C"), colors.HexColor("#5A6170")
FONDO_TABLA, BORDE = colors.HexColor("#EEF1F5"), colors.HexColor("#C9CFD8")

INTEGRANTES = {   # nombre de autor en Git -> integrante
    "Jean Salas Meneses": "Jean Salas Meneses",
    "jeanpaulsalasmeneses-lab": "Jean Salas Meneses",
    "Jairo Barraza": "Jairo Barraza Salazar",
    "jbarraza36": "Jairo Barraza Salazar",
    "Pavel Chávez San Martín": "Pavel Chávez San Martín",
    "Girosmedia": "Pavel Chávez San Martín",
    "girosmedia": "Pavel Chávez San Martín",
    "Javier Huamani": "Javier Huamani Barrera",
    "jav195": "Javier Huamani Barrera",
}
EQUIPO = ["Jairo Barraza Salazar", "Javier Huamani Barrera", "Jean Salas Meneses",
          "Pavel Chávez San Martín"]


# ==========================================================
# 1. FUENTES (Arial; en Linux, Liberation Sans tiene las mismas medidas)
# ==========================================================

def primera_existente(*rutas):
    for ruta in rutas:
        if Path(ruta).is_file():
            return str(ruta)
    raise FileNotFoundError(f"No se encontró ninguna de estas fuentes: {rutas}")


def registrar_fuentes():
    win, mac = Path("C:/Windows/Fonts"), Path("/Library/Fonts")
    lib = Path("/usr/share/fonts")
    sans = {
        "Arial": (win / "arial.ttf", mac / "Arial.ttf",
                  lib / "liberation-sans-fonts/LiberationSans-Regular.ttf",
                  lib / "truetype/liberation/LiberationSans-Regular.ttf"),
        "Arial-Bold": (win / "arialbd.ttf", mac / "Arial Bold.ttf",
                       lib / "liberation-sans-fonts/LiberationSans-Bold.ttf",
                       lib / "truetype/liberation/LiberationSans-Bold.ttf"),
        "Arial-Italic": (win / "ariali.ttf", mac / "Arial Italic.ttf",
                         lib / "liberation-sans-fonts/LiberationSans-Italic.ttf",
                         lib / "truetype/liberation/LiberationSans-Italic.ttf"),
        "Arial-BoldItalic": (win / "arialbi.ttf", mac / "Arial Bold Italic.ttf",
                             lib / "liberation-sans-fonts/LiberationSans-BoldItalic.ttf",
                             lib / "truetype/liberation/LiberationSans-BoldItalic.ttf"),
    }
    for nombre, rutas in sans.items():
        pdfmetrics.registerFont(TTFont(nombre, primera_existente(*rutas)))
    registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic",
                       boldItalic="Arial-BoldItalic")
    # Monoespaciada para código, y DejaVu Sans (incluida en matplotlib) para ①–⑥.
    mpl = Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf"
    pdfmetrics.registerFont(TTFont("Mono", primera_existente(
        win / "consola.ttf", lib / "liberation-mono-fonts/LiberationMono-Regular.ttf",
        lib / "truetype/liberation/LiberationMono-Regular.ttf", mpl / "DejaVuSansMono.ttf")))
    pdfmetrics.registerFont(TTFont("Simbolos", str(mpl / "DejaVuSans.ttf")))


# ==========================================================
# 2. DATOS DEL REPOSITORIO
# ==========================================================

def git(*args):
    # Git entrega UTF-8. Sin encoding explícito, Python decodifica con la codificación
    # del sistema (cp1252 en Windows) y «Chávez» deja de coincidir con INTEGRANTES.
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout.strip()


def tabla_commits():
    autores = Counter(INTEGRANTES.get(a, a) for a in git("log", "--no-merges",
                                                        "--format=%an").splitlines())
    filas = ["| Integrante | Commits (sin merges) |", "|---|---:|"]
    filas += [f"| {n} | {autores.get(n, 0)} |" for n in EQUIPO]
    otros = {a: c for a, c in autores.items() if a not in EQUIPO}
    filas += [f"| {a} (sin identificar) | {c} |" for a, c in otros.items()]
    filas.append(f"| **Total** | **{sum(autores.values())}** |")
    return "\n".join(filas)


# ==========================================================
# 3. ESTILOS (todo en 11 pt)
# ==========================================================

def estilos():
    base = dict(fontName="Arial", fontSize=LETRA, leading=13.6, textColor=AZUL)
    return {
        "p": ParagraphStyle("p", spaceAfter=4, **base),
        "li": ParagraphStyle("li", spaceAfter=1.5, bulletFontName="Arial", bulletFontSize=LETRA,
                             **base),
        "cita": ParagraphStyle("cita", fontName="Arial-Italic", fontSize=LETRA, leading=14.5,
                               textColor=AZUL, leftIndent=14, rightIndent=10, spaceBefore=4,
                               spaceAfter=8, borderPadding=(4, 0, 4, 8)),
        "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=15, leading=19,
                             textColor=AZUL, spaceBefore=10, spaceAfter=5),
        "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=12.5, leading=16,
                             textColor=AZUL, spaceBefore=8, spaceAfter=4),
        "titulo_indice": ParagraphStyle("titulo_indice", fontName="Arial-Bold", fontSize=15,
                                        leading=19, textColor=AZUL, spaceAfter=10),
        "celda": ParagraphStyle("celda", fontName="Arial", fontSize=LETRA, leading=12.8,
                                textColor=AZUL),
        "celda_h": ParagraphStyle("celda_h", fontName="Arial-Bold", fontSize=LETRA,
                                  leading=12.8, textColor=AZUL),
        "codigo": ParagraphStyle("codigo", fontName="Mono", fontSize=LETRA, leading=12.8,
                                 textColor=AZUL, backColor=FONDO_TABLA, borderPadding=6,
                                 spaceBefore=2, spaceAfter=7, leftIndent=6),
        "ref": ParagraphStyle("ref", fontName="Arial", fontSize=LETRA, leading=13.2,
                              textColor=AZUL, leftIndent=24, firstLineIndent=-24, spaceAfter=3),
        "pie": ParagraphStyle("pie", fontName="Arial-Italic", fontSize=LETRA, leading=13.5,
                              textColor=GRIS, spaceAfter=8),
        "toc1": ParagraphStyle("toc1", fontName="Arial-Bold", fontSize=LETRA, leading=14,
                               textColor=AZUL),
        "toc2": ParagraphStyle("toc2", fontName="Arial", fontSize=LETRA, leading=13.5,
                               leftIndent=18, textColor=AZUL),
    }


# ==========================================================
# 4. MARKDOWN -> FLOWABLES (subconjunto usado en el informe)
# ==========================================================

SIMBOLOS = "①②③④⑤⑥⑦⑧⑨"


def en_linea(texto):
    """Negrita, cursiva, código y símbolos -> marcado de reportlab."""
    texto = texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    trozos = re.split(r"(`[^`]+`)", texto)
    salida = []
    for t in trozos:
        if t.startswith("`") and t.endswith("`"):
            salida.append(f'<font name="Mono">{t[1:-1]}</font>')
            continue
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
        salida.append(t)
    texto = "".join(salida)
    return re.sub(f"([{SIMBOLOS}])", r'<font name="Simbolos">\1</font>', texto)


def tabla(lineas, est):
    filas = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lineas]
    alineacion = ["RIGHT" if c.strip().endswith(":") and not c.strip().startswith(":---")
                  and c.strip().startswith("-") else "LEFT" for c in filas[1]]
    filas = [filas[0]] + filas[2:]
    n = len(filas[0])
    limpio = lambda c: re.sub(r"[*`]", "", c)
    largo = [max(len(limpio(f[i])) for f in filas) for i in range(n)]
    # Ancho mínimo: la palabra más larga de la columna (en negrita, por si es encabezado).
    minimo = [max(stringWidth(w, "Arial-Bold", LETRA) for f in filas for w in limpio(f[i]).split()
                  or [""]) + 10 for i in range(n)]
    # Una ruta larga sin espacios no puede imponer su ancho: se parte (splitLongWords).
    minimo = [min(m, 0.30 * ANCHO_UTIL) for m in minimo]
    if sum(minimo) > ANCHO_UTIL:
        minimo = [m * ANCHO_UTIL / sum(minimo) for m in minimo]
    peso = [max(6, min(l, 60)) ** 0.75 for l in largo]
    anchos = [max(m, ANCHO_UTIL * p / sum(peso)) for m, p in zip(minimo, peso)]
    exceso = sum(anchos) - ANCHO_UTIL
    if exceso > 0:          # se descuenta de las columnas que superan su mínimo
        holgura = [a - m for a, m in zip(anchos, minimo)]
        anchos = [a - exceso * h / sum(holgura) for a, h in zip(anchos, holgura)]
    assert sum(anchos) <= ANCHO_UTIL + 1, "La tabla no cabe en el ancho de página."
    datos = [[Paragraph(en_linea(c), est["celda_h" if r == 0 else "celda"]) for c in f]
             for r, f in enumerate(filas)]
    t = Table(datos, colWidths=anchos, repeatRows=1, hAlign="LEFT")
    estilo = [("BACKGROUND", (0, 0), (-1, 0), FONDO_TABLA),
              ("LINEBELOW", (0, 0), (-1, 0), 1, AZUL),
              ("LINEBELOW", (0, 1), (-1, -1), 0.4, BORDE),
              ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
              ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    estilo += [("ALIGN", (i, 1), (i, -1), "RIGHT") for i, a in enumerate(alineacion)
               if a == "RIGHT"]
    t.setStyle(TableStyle(estilo))
    return [t, Spacer(1, 5)]


def bloque_codigo(lineas, est):
    disponible = ANCHO_UTIL - 2 * 6 - 6
    for l in lineas:
        ancho = stringWidth(l, "Mono", LETRA)
        assert ancho <= disponible, f"Línea de código fuera del margen ({ancho:.0f} pt): {l!r}"
    return [Preformatted("\n".join(lineas), est["codigo"])]


class Figura(Flowable):
    """Imagen al ancho útil con su pie debajo. Si no cabe en el espacio que queda
    en la página, se reduce hasta un 15 % antes de pasar a la página siguiente."""

    REDUCCION_MAXIMA = 0.85

    def __init__(self, ruta, pie):
        super().__init__()
        self.ruta, self.pie = str(ruta), pie
        ancho_px, alto_px = ImageReader(self.ruta).getSize()
        self.proporcion = alto_px / ancho_px

    def wrap(self, disponible_ancho, disponible_alto):
        _, alto_pie = self.pie.wrap(disponible_ancho, disponible_alto)
        self.alto_pie = alto_pie
        natural = disponible_ancho * self.proporcion
        escala = min(1.0, max(self.REDUCCION_MAXIMA,
                              (disponible_alto - alto_pie - 12) / natural))
        self.img_ancho = disponible_ancho * escala
        self.img_alto = natural * escala
        self.ancho = disponible_ancho
        return disponible_ancho, self.img_alto + 4 + alto_pie + 8

    def draw(self):
        x = (self.ancho - self.img_ancho) / 2
        self.canv.drawImage(self.ruta, x, self.alto_pie + 4 + 8, self.img_ancho, self.img_alto,
                            mask="auto")
        self.pie.drawOn(self.canv, 0, 8)


def markdown_a_flowables(md, est):
    lineas = md.splitlines()
    i, salida, parrafo = 0, [], []

    en_referencias = False

    def cerrar_parrafo():
        if parrafo:
            estilo = est["ref"] if en_referencias else est["p"]
            salida.append(Paragraph(en_linea(" ".join(parrafo)), estilo))
            parrafo.clear()

    while i < len(lineas):
        l = lineas[i]
        if l.startswith("```"):
            cerrar_parrafo()
            j = i + 1
            while not lineas[j].startswith("```"):
                j += 1
            salida += bloque_codigo(lineas[i + 1:j], est)
            i = j + 1
            continue
        if l.startswith("# "):
            cerrar_parrafo()
            # Sin keepWithNext: una tabla larga puede empezar bajo su título y seguir en
            # la página siguiente. El título solo salta si quedan menos de 80 pt.
            salida += [CondPageBreak(80), Paragraph(en_linea(l[2:]), est["h1"])]
            en_referencias = l.startswith("# 29.")
        elif l.startswith("## "):
            cerrar_parrafo()
            salida += [CondPageBreak(80), Paragraph(en_linea(l[3:]), est["h2"])]
        elif l.startswith("|"):
            cerrar_parrafo()
            j = i
            while j < len(lineas) and lineas[j].startswith("|"):
                j += 1
            salida += tabla(lineas[i:j], est)
            i = j
            continue
        elif l.startswith("> "):
            cerrar_parrafo()
            salida.append(Paragraph(en_linea(l[2:]), est["cita"]))
        elif m := re.match(r"!\[(.*)\]\((.*)\)", l):
            # La figura va dentro del texto, al ancho útil, con el pie debajo.
            cerrar_parrafo()
            salida.append(Figura(RAIZ / m.group(2), Paragraph(en_linea(m.group(1)), est["pie"])))
        elif m := re.match(r"^(\s*)(- |\d+\. )(.*)", l):
            cerrar_parrafo()
            nivel = len(m.group(1)) // 2
            vineta = "•" if m.group(2) == "- " else m.group(2).strip()
            estilo = ParagraphStyle(f"li{nivel}", parent=est["li"],
                                    leftIndent=16 + 16 * nivel, bulletIndent=4 + 16 * nivel)
            salida.append(Paragraph(en_linea(m.group(3)), estilo, bulletText=vineta))
        elif not l.strip():
            cerrar_parrafo()
        elif en_referencias and l.startswith("**"):
            cerrar_parrafo()
            salida.append(Paragraph(en_linea(l.strip()), est["p"]))
        else:
            parrafo.append(l.strip())
        i += 1
    cerrar_parrafo()
    return salida


# ==========================================================
# 5. DOCUMENTO: portada, índice automático y páginas
# ==========================================================

class Informe(BaseDocTemplate):
    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("h1", "h2"):
            nivel = 0 if f.style.name == "h1" else 1
            clave = f"h{id(f)}"
            self.canv.bookmarkPage(clave)
            self.canv.addOutlineEntry(f.getPlainText(), clave, level=nivel)
            self.notify("TOCEntry", (nivel, f.getPlainText(), self.page, clave))


def portada(canvas, doc):
    w, h = letter
    canvas.saveState()
    canvas.setFillColor(AZUL)
    canvas.rect(0, h - 0.5 * cm, w, 0.5 * cm, stroke=0, fill=1)
    canvas.setFillColor(ROJO)
    canvas.rect(0, h - 0.65 * cm, w, 0.15 * cm, stroke=0, fill=1)
    ancho_logo = 7.5 * cm
    canvas.drawImage(str(LOGO), MARGEN, h - 1.6 * cm - ancho_logo * 694 / 2070,
                     ancho_logo, ancho_logo * 694 / 2070, mask="auto")
    canvas.restoreState()


def pagina(canvas, doc):
    w, h = letter
    canvas.saveState()
    canvas.setStrokeColor(AZUL)
    canvas.setLineWidth(0.6)
    canvas.line(MARGEN, h - 1.3 * cm, w - MARGEN, h - 1.3 * cm)
    canvas.setFont("Arial", LETRA)
    canvas.setFillColor(GRIS)
    canvas.drawString(MARGEN, h - 1.1 * cm, "MCDI500 · Sumativa 3 · Grupo 7 · BORRADOR")
    canvas.drawRightString(w - MARGEN, 0.9 * cm, f"Página {doc.page}")
    canvas.restoreState()


def contenido_portada(est):
    p = lambda txt, **kw: Paragraph(txt, ParagraphStyle("x", parent=est["p"], **kw))
    return [
        Spacer(1, 4.2 * cm),
        p("Magíster en Ciencia de Datos e Inteligencia Artificial<br/>"
          "MCDI500 · Programación para la Ciencia de Datos", textColor=GRIS),
        Spacer(1, 0.8 * cm),
        p("EVALUACIÓN SUMATIVA 3 · FASE 4 · BORRADOR PARA REVISIÓN DEL GRUPO",
          fontName="Arial-Bold", textColor=ROJO),
        p("Informe final: proyecto integrador, reproducibilidad y comunicación de resultados",
          fontName="Arial-Bold", fontSize=17, leading=22),
        Spacer(1, 0.5 * cm),
        p("<b>Proyecto:</b> Exposición operacional documentada de las 15 comunas más pobladas "
          "de Chile a las fallas del Sistema Eléctrico Nacional (2024–2026)"),
        Spacer(1, 0.6 * cm),
        p("<b>Grupo 7</b><br/>" + "<br/>".join(EQUIPO)),
        Spacer(1, 0.4 * cm),
        p("<b>Docente:</b> Dr. Omar Salinas Silva"),
        p(f"<b>Fecha:</b> {date.today().day} de noviembre de {date.today().year}"),
        p(f"<b>Repositorio:</b> {REPO}"),
        NextPageTemplate("normal"),
        PageBreak(),
    ]


def main():
    registrar_fuentes()
    est = estilos()
    md = FUENTE_MD.read_text(encoding="utf-8")
    md = (md.replace("{{COMMIT}}", git("rev-parse", "--short", "HEAD"))
            .replace("{{TABLA_COMMITS}}", tabla_commits())
            .replace("{{REPO}}", REPO))
    assert "{{" not in md, "Quedó un marcador {{...}} sin reemplazar."

    doc = Informe(str(SALIDA), pagesize=letter, leftMargin=MARGEN, rightMargin=MARGEN,
                  topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                  title="f4_s04_grupo7 · Informe final Fase 4 (borrador)",
                  author="Grupo 7 · MCDI500", subject="Fase 4")
    marco = Frame(MARGEN, 1.8 * cm, ANCHO_UTIL, letter[1] - 3.6 * cm, id="marco")
    doc.addPageTemplates([PageTemplate("portada", [marco], onPage=portada),
                          PageTemplate("normal", [marco], onPage=pagina)])
    sin_relleno = TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")] + [
        (lado, (0, 0), (-1, -1), 0) for lado in ("TOPPADDING", "BOTTOMPADDING",
                                                 "LEFTPADDING", "RIGHTPADDING")])
    indice = TableOfContents(levelStyles=[est["toc1"], est["toc2"]], dotsMinLevel=0,
                             tableStyle=sin_relleno)
    historia = contenido_portada(est)
    historia += [Paragraph("Índice", est["titulo_indice"]), indice, Spacer(1, 10)]
    historia += markdown_a_flowables(md, est)
    doc.multiBuild(historia)
    verificar_tamanos()
    assert doc.page <= MAX_PAGINAS, f"El PDF tiene {doc.page} páginas; el máximo es {MAX_PAGINAS}."
    print(f"OK {SALIDA.name} · {doc.page} páginas · todo el texto en {LETRA} pt o más")


def verificar_tamanos():
    """Recorre el PDF generado y falla si algún texto tiene menos de LETRA pt."""
    from pypdf import PdfReader
    chicos = []
    for numero, pagina_pdf in enumerate(PdfReader(SALIDA).pages, 1):
        def visitar(texto, cm_, tm, fd, fs):
            tamano = fs * tm[0] if tm[0] else fs
            if texto.strip() and tamano < LETRA - 0.05:
                chicos.append((numero, texto.strip()[:30], round(tamano, 1)))
        pagina_pdf.extract_text(visitor_text=visitar)
    assert not chicos, f"Textos con menos de {LETRA} pt: {chicos[:10]}"


if __name__ == "__main__":
    main()
