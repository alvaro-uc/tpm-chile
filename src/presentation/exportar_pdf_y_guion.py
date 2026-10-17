"""Exporta láminas y guion de ensayo desde el PPTX ya renderizado y su contenido."""
import json
import re
import sys
from html import escape
from pathlib import Path

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from pypdf import PdfReader
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / '.build/presentacion'
OUT = ROOT / 'output/pdf'
OUT.mkdir(parents=True, exist_ok=True)
CONTENT = json.loads((ROOT / 'src/presentation/contenido_video.json').read_text(encoding='utf-8'))
INK = HexColor('#172B42')
GRAY = HexColor('#64748B')
BLUE = HexColor('#2364AA')
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold', 'C:/Windows/Fonts/arialbd.ttf'))


def stamp(seconds):
    return f'{seconds//60}:{seconds%60:02d}'


def paragraph(canvas, text, x, top, width, size=11, color=INK, leading=None, bold=False):
    style = ParagraphStyle('p', fontName='ArialBold' if bold else 'Arial', fontSize=size,
                           leading=leading or size*1.35, textColor=color)
    p = Paragraph(escape(text).replace('\n', '<br/>'), style)
    _, height = p.wrap(width, 1000)
    if top-height < 28:
        raise ValueError(f'Desborde de texto: {text[:50]}')
    p.drawOn(canvas, x, top-height)
    return height


def main(revision='v1'):
    if not re.fullmatch(r'v\d+', revision):
        raise ValueError('Revisión esperada: v1, v2, ...')
    slides = CONTENT['slides']
    total = sum(s['segundos'] for s in slides)
    words = sum(len(s['hablado'].split()) for s in slides)
    assert total == CONTENT['duracion_objetivo_segundos'] == 340
    images = [BUILD / f'final/slide-{i}.png' for i in range(1, 9)]
    assert all(p.exists() for p in images)
    pdf_path = OUT / f'avance_tpm_6_min_{revision}.pdf'
    c = Canvas(str(pdf_path), pagesize=(960, 540))
    c.setTitle('Avance TPM 2010-2025 - láminas para grabación')
    c.setAuthor('Grupo 9 - IMT2200')
    for image in images:
        c.drawImage(str(image), 0, 0, 960, 540, preserveAspectRatio=True)
        c.showPage()
    c.save()

    guion_path = OUT / f'guion_presentador_tpm_{revision}.pdf'
    c = Canvas(str(guion_path), pagesize=landscape(A4))
    c.setTitle('Guion del presentador - video de avance TPM')
    c.setAuthor('Grupo 9 - IMT2200')
    width, height = landscape(A4)
    elapsed = 0
    for s, image in zip(slides, images):
        titleheight = paragraph(c, f"{s['numero']}. {s['titulo']}", 36, height-28, width-72, 20, bold=True)
        subtitle_top = height-42-titleheight
        paragraph(c, f"{stamp(elapsed)}-{stamp(elapsed+s['segundos'])}   Voz propuesta: {s['voz']}   {s['segundos']} s", 36, subtitle_top, width-72, 11, GRAY)
        elapsed += s['segundos']
        thumb_top = subtitle_top-31
        c.drawImage(str(image), 36, thumb_top-210, 374, 210.375, preserveAspectRatio=True)
        spoken_top = thumb_top
        h = paragraph(c, 'Texto para ensayar', 444, spoken_top, 360, 12, BLUE, bold=True)
        spoken_h = paragraph(c, s['hablado'], 444, spoken_top-h-12, 360, 11.5, INK, 15.8)
        cue_top = thumb_top-230
        h = paragraph(c, 'Qué señalar con el puntero', 36, cue_top, 374, 12, BLUE, bold=True)
        paragraph(c, s['puntero'], 36, cue_top-h-10, 374, 11, INK, 14.5)
        # El localizador y las URLs completas también quedan en las notas y en el Markdown.
        source_text = '\n'.join(s['fuentes'][:2])
        paragraph(c, 'Fuentes\n'+source_text, 444, min(155,spoken_top-h-12-spoken_h-24), 360, 8, GRAY, 10)
        c.setFont('Arial', 8.5);c.setFillColor(GRAY)
        c.drawString(36, 21, f'Objetivo de ensayo: 5:40. Reservar margen hasta 6:00. Notas completas en PowerPoint y guion editable.')
        c.drawRightString(width-36, 21, f'{s["numero"]} / 8')
        c.showPage()
    c.save()

    md = [
        '# Guion para el video de avance del proyecto de TPM',
        '', '**Entrega 2 · IMT2200 · Grupo 9 · Versión coordinada al 17-10-2026**', '',
        f'Presentación de **8 diapositivas**. Objetivo de ensayo: **5:40**. Margen hasta **6:00**. '
        f'El texto hablado contiene **{words} palabras**, equivalente a unas {round(words/total*60)} por minuto si ocupa todo el tiempo. '
        'El ritmo real y los gestos deben ensayarse con cronómetro. Los tiempos incluyen el cambio de lámina. '
        'Las acotaciones y las fuentes no se leen en voz alta.', '',
        'Este guion sigue la consigna descrita por el usuario: problemática, preguntas, descripción de datos, '
        'análisis realizados y avances, en un video de aproximadamente seis minutos. No constituye una revisión independiente de Canvas.', '',
        'El reparto de voces es una propuesta. Cada persona presenta dos láminas consecutivas. '
        'Si graba una sola persona, conservar el orden y los tiempos.', '',
        '| Lámina | Tiempo | Voz propuesta | Tema |', '|---|---|---|---|',
    ]
    elapsed = 0
    for s in slides:
        md.append(f"| {s['numero']} | {stamp(elapsed)}-{stamp(elapsed+s['segundos'])} | {s['voz']} | {s['titulo']} |")
        elapsed += s['segundos']
    elapsed = 0
    for s in slides:
        md.extend(['', f"## Diapositiva {s['numero']}: {s['titulo']}", '',
                   f"**{stamp(elapsed)}-{stamp(elapsed+s['segundos'])} · {s['voz']} · {s['segundos']} segundos**", '',
                   '**Texto hablado**', '', s['hablado'], '', '**Puntero y pantalla**', '', s['puntero'], '', '**Fuentes**', ''])
        md.extend('- '+source for source in s['fuentes'])
        elapsed += s['segundos']
    md.extend(['', '## Preparación de la grabación', '',
        'Abrir el PDF de láminas en Xournal++ y mantener este guion fuera de la región capturada. '
        'En PowerPoint, las mismas indicaciones quedan en las notas de cada diapositiva. '
        'Grabar una prueba breve con micrófono y puntero antes de hacer la toma completa. '
        'El PDF de láminas no contiene narración ni animación pregrabada.', '',
        'Usar el puntero para fechas, valores y relaciones concretas. Evitar moverlo continuamente mientras se habla. '
        'Dejar que el rastro desaparezca antes de señalar otra parte de la figura.', '',
        'Si el ensayo supera seis minutos, resumir primero el detalle de IPC anual en la lámina 2 y '
        'los comentarios descriptivos de la trayectoria en la lámina 4. Mantener la pregunta, los conteos, '
        'la explicación del corte, los vínculos y la distinción entre avance y resultados de modelos.', '',
        '## Cifras y límites que deben coincidir', '',
        '- 2010–2025, con 161 decisiones: 103 mantiene, 31 baja y 27 sube.',
        '- 103/161 = 63,98%, redondeado a 64%. Es descriptivo sobre el registro completo.',
        '- Cobre: Cochilco spot BML/LME, USD/libra y 4.042 cotizaciones.',
        '- Reunión 17/10/2024, corte 16/10. IPC septiembre 0,1%, publicado 08/10. Octubre publicado 08/11.',
        '- Cuatro boletines IPC verificados como ejemplo. Calendario completo de ocho series aún pendiente.',
        '- La trayectoria y la distribución son resultados descriptivos. No hay métricas de modelos.',
        '- El calendario operativo requiere contraste bancario y los datos revisables requieren versiones históricas.',
        '', '## Edición coordinada', '',
        'El texto hablado, tiempos, voces y fuentes se mantienen en `src/presentation/contenido_video.json`. '
        'Al cambiarlo, regenerar la presentación, sus notas y este guion en la misma revisión. '
        'Los scripts y comandos están en `src/presentation/README.md`.', ''])
    (ROOT / 'docs/guion_video_avance_entrega_2.md').write_text('\n'.join(md), encoding='utf-8')
    assert len(PdfReader(str(pdf_path)).pages) == len(PdfReader(str(guion_path)).pages) == 8
    # Vista general interna para revisar la secuencia.
    montage = Image.new('RGB', (1280, 1440), 'white')
    for i, image in enumerate(images):
        im = Image.open(image).convert('RGB');im.thumbnail((640, 360))
        montage.paste(im, ((i%2)*640, (i//2)*360))
    montage.save(BUILD / 'montaje.png')
    print(json.dumps({'laminas':str(pdf_path),'guion':str(guion_path),'paginas':8,'palabras':words,'segundos_objetivo':total}, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv)>1 else 'v1')
