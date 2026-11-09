"""
Genera el informe técnico de la Sumativa 1 (PDF) desde informe_sumativa1.md.

Uso, desde la raíz del proyecto y con el .venv activo:

    python -m pip install -r docs/entregas/sumativa1/requirements-informe.txt
    python docs/entregas/sumativa1/generar_informe.py

- El texto del informe se edita SOLO en informe_sumativa1.md. Este script le
  da formato: portada institucional, índice automático desde los títulos,
  tamaño carta, Arial 11 pt en todo el documento y numeración de páginas.
- Los datos del repositorio ({{COMMIT}}, {{TABLA_COMMITS}}, {{REPO}}) se
  calculan con Git al generar el PDF, para que el informe no quede
  desactualizado respecto del historial.
- Verifica con assert que ningún bloque de código o tabla se salga del margen.

Salida: docs/entregas/sumativa1/mcdi500_s1_grupo7.pdf
(convención del curso: mcdi500_s1_grupox, sin tildes, máximo 20 caracteres).
"""

import re
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily, stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Preformatted, Spacer, Table,
                                TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
FUENTE_MD = AQUI / "informe_sumativa1.md"
LOGO = AQUI / "logo_unab.png"
SALIDA = AQUI / "mcdi500_s1_grupo7.pdf"
REPO = "https://github.com/jeanpaulsalasmeneses-lab/Proyecto_MCDI500"

LETRA = 11                      # tamaño mínimo y general del documento
MARGEN = 2.2 * cm
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
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True,
                          check=True).stdout.strip()


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
    base = dict(fontName="Arial", fontSize=LETRA, leading=14.5, textColor=AZUL)
    return {
        "p": ParagraphStyle("p", spaceAfter=6, **base),
        "li": ParagraphStyle("li", spaceAfter=3, bulletFontName="Arial", bulletFontSize=LETRA,
                             **base),
        "cita": ParagraphStyle("cita", fontName="Arial-Italic", fontSize=LETRA, leading=14.5,
                               textColor=AZUL, leftIndent=14, rightIndent=10, spaceBefore=4,
                               spaceAfter=8, borderPadding=(4, 0, 4, 8)),
        "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=15, leading=19,
                             textColor=AZUL, spaceBefore=16, spaceAfter=8, keepWithNext=1),
        "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=12.5, leading=16,
                             textColor=AZUL, spaceBefore=10, spaceAfter=5, keepWithNext=1),
        "titulo_indice": ParagraphStyle("titulo_indice", fontName="Arial-Bold", fontSize=15,
                                        leading=19, textColor=AZUL, spaceAfter=10),
        "celda": ParagraphStyle("celda", fontName="Arial", fontSize=LETRA, leading=13.5,
                                textColor=AZUL),
        "celda_h": ParagraphStyle("celda_h", fontName="Arial-Bold", fontSize=LETRA,
                                  leading=13.5, textColor=AZUL),
        "codigo": ParagraphStyle("codigo", fontName="Mono", fontSize=LETRA, leading=13.5,
                                 textColor=AZUL, backColor=FONDO_TABLA, borderPadding=6,
                                 spaceBefore=4, spaceAfter=10, leftIndent=6),
        "ref": ParagraphStyle("ref", fontName="Arial", fontSize=LETRA, leading=14.5,
                              textColor=AZUL, leftIndent=24, firstLineIndent=-24, spaceAfter=7),
        "pie": ParagraphStyle("pie", fontName="Arial-Italic", fontSize=LETRA, leading=14,
                              textColor=GRIS, alignment=TA_CENTER, spaceAfter=8),
        "toc1": ParagraphStyle("toc1", fontName="Arial-Bold", fontSize=LETRA, leading=17,
                               textColor=AZUL),
        "toc2": ParagraphStyle("toc2", fontName="Arial", fontSize=LETRA, leading=15,
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
              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
              ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    estilo += [("ALIGN", (i, 1), (i, -1), "RIGHT") for i, a in enumerate(alineacion)
               if a == "RIGHT"]
    t.setStyle(TableStyle(estilo))
    return [t, Spacer(1, 8)]


def bloque_codigo(lineas, est):
    disponible = ANCHO_UTIL - 2 * 6 - 6
    for l in lineas:
        ancho = stringWidth(l, "Mono", LETRA)
        assert ancho <= disponible, f"Línea de código fuera del margen ({ancho:.0f} pt): {l!r}"
    return [KeepTogether([Preformatted("\n".join(lineas), est["codigo"])])]


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
            # Página nueva solo para Referencias y anexos; el resto fluye.
            if (salida and not isinstance(salida[-1], PageBreak)
                    and (l.startswith("# 14.") or l.startswith("# Anexo"))):
                salida.append(PageBreak())
            salida.append(Paragraph(en_linea(l[2:]), est["h1"]))
            en_referencias = l.startswith("# 14. Referencias")
        elif l.startswith("## "):
            cerrar_parrafo()
            salida.append(Paragraph(en_linea(l[3:]), est["h2"]))
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
            # La figura va sola en una página horizontal a tamaño real (11 x 8,5 in),
            # para que su texto conserve los 11 pt con que se generó.
            cerrar_parrafo()
            salida.append(Paragraph(en_linea(m.group(1)), est["pie"]))
            img = Image(str(RAIZ / m.group(2)), width=11 * 72, height=8.5 * 72)
            salida += [NextPageTemplate("figura"), PageBreak(), img,
                       NextPageTemplate("normal"), PageBreak()]
        elif m := re.match(r"^(\s*)(- |\d+\. )(.*)", l):
            cerrar_parrafo()
            nivel = len(m.group(1)) // 2
            vineta = "•" if m.group(2) == "- " else m.group(2).strip()
            estilo = ParagraphStyle(f"li{nivel}", parent=est["li"],
                                    leftIndent=16 + 16 * nivel, bulletIndent=4 + 16 * nivel)
            salida.append(Paragraph(en_linea(m.group(3)), estilo, bulletText=vineta))
        elif not l.strip():
            cerrar_parrafo()
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
    canvas.line(MARGEN, h - 1.4 * cm, w - MARGEN, h - 1.4 * cm)
    canvas.setFont("Arial", LETRA)
    canvas.setFillColor(GRIS)
    canvas.drawString(MARGEN, h - 1.2 * cm, "MCDI500 · Sumativa 1 · Grupo 7")
    canvas.drawRightString(w - MARGEN, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def contenido_portada(est):
    p = lambda txt, **kw: Paragraph(txt, ParagraphStyle("x", parent=est["p"], **kw))
    return [
        Spacer(1, 4.2 * cm),
        p("Magíster en Ciencia de Datos e Inteligencia Artificial<br/>"
          "MCDI500 · Programación para la Ciencia de Datos", textColor=GRIS),
        Spacer(1, 0.8 * cm),
        p("EVALUACIÓN SUMATIVA 1 · FASES 1 Y 2", fontName="Arial-Bold", textColor=ROJO),
        p("Informe técnico: implementación inicial del entorno reproducible, exploración y "
          "procesamiento inicial de los datos", fontName="Arial-Bold", fontSize=17, leading=22),
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
                  topMargin=2 * cm, bottomMargin=2 * cm,
                  title="mcdi500_s1_grupo7 · Informe técnico Sumativa 1",
                  author="Grupo 7 · MCDI500", subject="Fases 1 y 2")
    marco = Frame(MARGEN, 2 * cm, ANCHO_UTIL, letter[1] - 4 * cm, id="marco")
    pagina_figura = Frame(0, 0, *landscape(letter), leftPadding=0, rightPadding=0,
                          topPadding=0, bottomPadding=0, id="figura")
    doc.addPageTemplates([PageTemplate("portada", [marco], onPage=portada),
                          PageTemplate("normal", [marco], onPage=pagina),
                          PageTemplate("figura", [pagina_figura], pagesize=landscape(letter))])
    indice = TableOfContents(levelStyles=[est["toc1"], est["toc2"]], dotsMinLevel=0)
    historia = contenido_portada(est)
    historia += [Paragraph("Índice", est["titulo_indice"]), indice, PageBreak()]
    historia += markdown_a_flowables(md, est)
    doc.multiBuild(historia)
    verificar_tamanos()
    print(f"OK {SALIDA.relative_to(RAIZ)} · {doc.page} páginas · todo el texto en {LETRA} pt o más")


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
