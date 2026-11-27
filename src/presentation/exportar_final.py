"""Exporta las láminas para OBS y los guiones sincronizados del video final."""
from html import escape
import json
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / ".build/entrega_final"
OUT = ROOT / "output/entrega_final"
INK = HexColor("#172B42")
BLUE = HexColor("#2364AA")
GRAY = HexColor("#526478")


def tiempo(s):
    return f"{s // 60}:{s % 60:02d}"


def parrafo(canvas, texto, x, y, ancho, size, bold=False, color=INK):
    familia = "Arial Bold" if bold else "Arial"
    estilo = ParagraphStyle("texto", fontName=familia, fontSize=size,
                            leading=size * 1.34, textColor=color)
    bloque = Paragraph(escape(texto), estilo)
    _, alto = bloque.wrap(ancho, y)
    if y - alto < 42:
        raise ValueError(f"Texto fuera de página: {texto[:50]}")
    bloque.drawOn(canvas, x, y - alto)
    return y - alto


def exportar_pauta(slides, total):
    pdf = Canvas(str(OUT / "pauta_grabacion.pdf"), pagesize=A4)
    pdf.setTitle("Pauta de grabación y edición | TPM en Chile")
    pdf.setAuthor("Grupo 9 · IMT2200")
    margen = 43
    ancho = A4[0] - 2 * margen
    parrafo(pdf, "IMT2200  /  GRUPO 9", margen, 800, ancho, 10, bold=True, color=BLUE)
    parrafo(pdf, "Pauta de grabación y edición", margen, 775, ancho, 28, bold=True)
    parrafo(pdf, f"{len(slides)} láminas  ·  {tiempo(total)} de ensayo  ·  ¿Podemos anticipar al Banco Central?",
            margen, 729, ancho, 11, color=GRAY)
    parrafo(pdf, "1. Abre 01_Laminas_para_OBS.pdf y 02_Guion_de_lectura.pdf en ventanas distintas. "
            "En OBS captura solo la ventana de las láminas, en 16:9.", margen, 701, ancho, 11)
    parrafo(pdf, "2. Graba 20 segundos de prueba y cambia de lámina. Comprueba la voz, "
            "la legibilidad del gráfico y que el guion quede fuera de la captura.", margen, 665, ancho, 11)
    parrafo(pdf, "3. Avanza una lámina por página del guion. Haz una pausa para repetir una frase "
            "si te trabas. El reparto de voces es opcional.", margen, 629, ancho, 11)

    parrafo(pdf, "Cambios de lámina y marcas opcionales", margen, 583, ancho, 16, bold=True)
    y = 552
    inicio = 0
    for i, slide in enumerate(slides, 1):
        pdf.setStrokeColor(HexColor("#CFDDEB"))
        pdf.line(margen, y, margen + ancho, y)
        parrafo(pdf, f"{tiempo(inicio)}  ·  {slide['voz']}", margen + 2, y - 4, 104, 10,
                bold=True, color=BLUE)
        parrafo(pdf, f"{i}. {slide['titulo']}", margen + 107, y - 4, ancho - 107, 10.6, bold=True)
        fin_fila = parrafo(pdf, slide["tecnico"], margen + 107, y - 18, ancho - 107, 9.6, color=GRAY)
        if fin_fila < y - 44:
            raise ValueError(f"La indicación de la lámina {i} supera su espacio en la pauta")
        y -= 40
        inicio += slide["segundos"]

    pdf.line(margen, y, margen + ancho, y)
    parrafo(pdf, "Edición. Usa cortes limpios y recuadros breves cuando se mencione el dato. "
            "Mantén visibles ejes, leyendas y cifras. Sincroniza con los tiempos de la toma.", margen, 102, ancho, 10)
    parrafo(pdf, "Exportación. Revisa audio, legibilidad y duración según Canvas. Guarda "
            "IMT2200_Grupo9_Video_Final.mp4 dentro de 02_ENTREGA.", margen, 69, ancho, 10)
    pdf.showPage()
    pdf.save()


def main():
    fuente = Path(__file__).with_name("contenido_final.json")
    slides = json.loads(fuente.read_text(encoding="utf-8"))
    pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial Bold", "C:/Windows/Fonts/arialbd.ttf"))
    tiempo_total = sum(slide["segundos"] for slide in slides)
    palabras = sum(len(slide["hablado"].split()) for slide in slides)
    lam = Canvas(str(OUT / "laminas_para_grabar.pdf"), pagesize=(960, 540), pageCompression=1)
    lam.setTitle("Decisiones de TPM en Chile | Láminas para grabar")
    voz = Canvas(str(OUT / "guion_de_lectura.pdf"), pagesize=(800, 760), pageCompression=1)
    voz.setTitle("Guion de lectura | TPM en Chile")
    for c in (lam, voz):
        c.setAuthor("Grupo 9 · IMT2200")

    tecnico = [
        "# Guion técnico de grabación y edición",
        "",
        f"Pauta de {tiempo(tiempo_total)} y {palabras} palabras habladas. "
        "Los tiempos son puntos de partida para el ensayo y se reajustan sobre la toma elegida. "
        "El reparto entre integrantes es propuesto. Una voz puede grabar toda la presentación.",
        "",
        "Abre [las láminas para OBS](laminas_para_grabar.pdf) y [el guion de lectura](guion_de_lectura.pdf) "
        "en ventanas separadas. La [pauta de grabación](pauta_grabacion.pdf) describe la prueba de captura.",
        "",
    ]
    elapsed = 0
    for i, slide in enumerate(slides, 1):
        imagen = BUILD / f"slide-{i:02d}.png"
        lam.drawImage(str(imagen), 0, 0, 960, 540)
        lam.showPage()
        rango = f"{tiempo(elapsed)}–{tiempo(elapsed + slide['segundos'])}"
        voz.setFillColor(BLUE)
        voz.setFont("Arial Bold", 14)
        voz.drawString(49, 717, f"Lámina {i} de {len(slides)}     {rango}     {slide['voz']}")
        voz.setStrokeColor(HexColor("#CFDDEB"))
        voz.line(49, 694, 751, 694)
        top = parrafo(voz, slide["titulo"], 49, 673, 702, 32, bold=True) - 21
        notas = slide.get("nota_expositor", [])
        for bloque in slide["hablado"].split("\n\n"):
            top = parrafo(voz, bloque, 49, top, 702, 21 if notas else 22) - 11
        if notas:
            voz.line(49, top, 751, top)
            top = parrafo(voz, "Apoyo para el expositor", 49, top - 10, 702, 14, bold=True, color=BLUE) - 4
            for nota in notas:
                top = parrafo(voz, nota, 49, top, 702, 14, color=GRAY) - 5
        voz.setFillColor(GRAY)
        voz.setFont("Arial", 12)
        voz.drawString(49, 31, f"Pauta total {tiempo(tiempo_total)}  ·  Cambia la lámina y el guion juntos.")
        voz.showPage()
        tecnico.extend([
            f"## {i}. {slide['titulo']}", "",
            f"**{rango} · {slide['segundos']} s · Voz propuesta: {slide['voz']}.**", "",
            slide["tecnico"], "",
            f"**Texto hablado.** {slide['hablado']}", "",
        ])
        if notas:
            tecnico.extend(["**Apoyo para el expositor.**", "", *[f"- {nota}" for nota in notas], ""])
        tecnico.extend(["**Referencia para cotejar.** " + " · ".join(slide["fuentes"]), ""])
        elapsed += slide["segundos"]

    lam.save()
    voz.save()
    exportar_pauta(slides, tiempo_total)
    (OUT / "guion_tecnico.md").write_text("\n".join(tecnico), encoding="utf-8")
    print(f"{len(slides)} láminas, {palabras} palabras, {tiempo(tiempo_total)} de pauta")


if __name__ == "__main__":
    main()
