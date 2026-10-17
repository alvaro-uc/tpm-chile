"""Secuencia explicativa con datos reales, exportable como PNG y desde notebook."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import pandas as pd

INK, BLUE, GREEN, RED, GRAY = '#172b42', '#2364aa', '#16765b', '#b63f45', '#64748b'


def base(title, subtitle):
    fig = plt.figure(figsize=(14, 8), facecolor='#fbfcfe')
    fig.text(.06, .94, title, fontsize=23, weight='bold', color=INK)
    fig.text(.06, .885, subtitle, fontsize=12, color=GRAY)
    return fig


def footer(fig, text):
    fig.text(.06, .045, text, fontsize=10, color=GRAY)


def box(ax, x, y, w, h, text, color=BLUE, size=12):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.015',
                              facecolor='white', edgecolor=color, linewidth=1.4))
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=size,
            color=INK, linespacing=1.7)


def generar_figuras(root, reuniones, datasets):
    """Guarda cuatro láminas y una vista conjunta, sin representar fechas supuestas."""
    out = Path(root) / 'docs/figures/integracion'
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    fig = base('1 · Una tasa diaria no identifica todas las reuniones',
               'Chile, abril–junio de 2010 · La línea registra el nivel; los marcadores identifican decisiones oficiales.')
    ax = fig.add_axes([.08, .25, .86, .53])
    daily = datasets['tpm_bcentral_diaria']
    sample = daily.loc[daily.fecha.between('2010-04-01', '2010-06-30')]
    ax.step(sample.fecha, sample.tpm_bcentral_diaria, where='post', color=BLUE, lw=3)
    selected = reuniones.loc[reuniones.fecha_decision.between('2010-04-01', '2010-06-30')]
    for row in selected.itertuples():
        keep = row.decision == 'mantiene'
        ax.scatter(row.fecha_decision, row.tpm_previa_pct, s=110,
                   marker='o' if keep else '^', color=GREEN if keep else BLUE, zorder=5)
        label = row.fecha_decision.strftime('%d/%m') + (' · mantiene 0,50%' if keep else ' · anuncia subida a 1,00%')
        offset = (-70, 55) if keep else (-185, 110)
        ax.annotate(label, (row.fecha_decision, row.tpm_previa_pct), xytext=offset,
                    textcoords='offset points', fontsize=11, color=INK,
                    arrowprops=dict(arrowstyle='-', color=GRAY))
    ax.set_ylim(.3, 1.5)
    ax.set_ylabel('TPM (%)', color=INK)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', alpha=.15)
    fig.text(.08, .145, 'El tramo plano incluye dos reuniones de mantención: no hay un salto que permita detectarlas.\n'
             'La subida se anuncia el 15/06; la serie diaria registra el nuevo nivel desde la observación del 16/06.',
             fontsize=13, color=INK, linespacing=1.7)
    footer(fig, 'Fuentes locales: reuniones TPM documentadas y serie diaria BCCh. Fecha de anuncio ≠ primera observación posterior.')
    path = out / '01_tpm_diaria_y_reuniones.png'
    fig.savefig(path, dpi=150); plt.close(fig); paths.append(path)

    fig = base('2 · Importa cuándo se publicó, además del mes medido',
               'Caso real: decisión de TPM del 17/10/2024 · Información permitida hasta el cierre del 16/10/2024.')
    ax = fig.add_axes([.08, .25, .86, .53])
    cut = pd.Timestamp('2024-10-16')
    decision = pd.Timestamp('2024-10-17')
    ax.axvspan(pd.Timestamp('2024-08-01'), cut, color=GREEN, alpha=.055)
    ax.axvspan(cut, pd.Timestamp('2024-11-17'), color=RED, alpha=.045)
    facts = [('2024-08-01', '2024-08-31', '2024-09-06', .3, 3, 'agosto'),
             ('2024-09-01', '2024-09-30', '2024-10-08', .1, 2, 'septiembre'),
             ('2024-10-01', '2024-10-31', '2024-11-08', 1., 1, 'octubre')]
    for start, end, release, value, y, month in facts:
        start, end, release = map(pd.Timestamp, [start, end, release])
        color = GREEN if release <= cut else RED
        ax.plot([start, end], [y, y], lw=10, solid_capstyle='butt', color=GRAY, alpha=.35)
        ax.annotate('', (release, y), (end, y), arrowprops=dict(arrowstyle='->', color=color, lw=1.8))
        ax.scatter(release, y, color=color, s=90, zorder=5, marker='o' if release <= cut else 'X')
        ax.text(start, y+.26, f'IPC de {month}', fontsize=12, color=INK)
        ax.text(release, y-.35, release.strftime('%d/%m') + ' · ' + str(value).replace('.', ',') + '%',
                ha='center', fontsize=11, color=INK)
    ax.axvline(cut, color=INK, ls='--', lw=1.5)
    ax.annotate('16/10 · corte\n17/10 · decisión TPM', (decision, 3.55),
                xytext=(35, 10), textcoords='offset points', color=INK, fontsize=11,
                arrowprops=dict(arrowstyle='-', color=GRAY))
    ax.set_ylim(.3, 4.2)
    ax.set_xlim(pd.Timestamp('2024-07-29'), pd.Timestamp('2024-11-17'))
    ax.set_yticks([])
    ticks = pd.to_datetime(['2024-08-01', '2024-09-01', '2024-10-01', '2024-11-01'])
    ax.set_xticks(ticks, ['01 agosto', '01 septiembre', '01 octubre', '01 noviembre'])
    ax.spines[['top', 'left', 'right']].set_visible(False)
    fig.text(.08, .15, 'Se utiliza el IPC de septiembre: 0,1%, publicado el 08/10.\n'
             'El IPC de octubre, 1,0%, existe en el archivo actual, pero aún no era público al corte.',
             fontsize=13, color=INK, linespacing=1.7)
    footer(fig, 'Barras: período medido. Puntos: publicación. Fuentes: boletines INE 310, 311 y 312; reunión BCCh del 17/10/2024.')
    path = out / '02_ipc_periodo_y_publicacion.png'
    fig.savefig(path, dpi=150); plt.close(fig); paths.append(path)

    fig = base('3 · Los identificadores conectan cada decisión con su dato',
               'Se vincula por disponibilidad al corte; el número de fila o el mes calendario no determinan la unión.')
    ax = fig.add_axes([.05, .13, .9, .68]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    box(ax, .025, .47, .25, .36, 'REUNIÓN\nRPM_20241017\nAnuncio: 17/10/2024\nCorte: 16/10/2024')
    box(ax, .375, .47, .25, .36, 'VÍNCULO\nRPM_20241017\n+ IPC de septiembre\nPublicación: 08/10/2024', GREEN)
    box(ax, .725, .47, .25, .36, 'OBSERVACIÓN ELEGIDA\nPeríodo: septiembre 2024\nValor publicado: 0,1%\nDisponible antes del corte', GREEN, 11)
    for x1, x2 in [(.28, .35), (.64, .71)]:
        ax.annotate('', (x2, .65), (x1, .65), arrowprops=dict(arrowstyle='->', color=BLUE, lw=2))
    box(ax, .025, .04, .95, .25, 'FILA PARA EL MODELO\n'
        'RPM_20241017    |    corte 16/10/2024    |    X: IPC mensual = 0,1%    |    y: baja\n'
        'X usa información anterior; y se obtiene del resultado de la reunión.', BLUE, 12)
    footer(fig, 'ID del dato: ipc_general_mensual_20240901. El mismo dato puede vincularse a más de una reunión.')
    path = out / '03_vinculo_y_fila_modelo.png'
    fig.savefig(path, dpi=150); plt.close(fig); paths.append(path)

    fig = base('4 · La muestra de decisiones abarca 2010–2025',
               'Recortamos las copias de trabajo; las descargas originales conservan su cobertura completa.')
    ax = fig.add_axes([.05, .14, .9, .66]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    box(ax, .02, .52, .29, .3, 'FUENTES ORIGINALES\nTPM desde 1997\nIPC mensual desde 1928\nCobre Cochilco desde 2010', GRAY)
    box(ax, .4, .52, .57, .3, 'COPIAS PARA EL ANÁLISIS\nDecisiones y vistas principales: 2010–2025\nSin registros posteriores a diciembre de 2025', BLUE, 14)
    ax.annotate('', (.38, .67), (.33, .67), arrowprops=dict(arrowstyle='->', color=BLUE, lw=2))
    box(ax, .4, .03, .57, .3, 'ANTECEDENTES: SOLO 2009\nReserva para obtener el último dato publicado\nantes de las primeras decisiones de 2010.\nNo añade decisiones de 2009 a la muestra.', GREEN)
    ax.annotate('', (.68, .49), (.68, .35), arrowprops=dict(arrowstyle='->', color=GREEN, lw=2))
    footer(fig, 'La reserva de 2009 es técnica; los faltantes de las fuentes no se rellenan con datos posteriores.')
    path = out / '04_ventana_2010_2025.png'
    fig.savefig(path, dpi=150); plt.close(fig); paths.append(path)

    from PIL import Image
    thumbs = [Image.open(p).convert('RGB') for p in paths]
    combined = Image.new('RGB', (1680, 960), '#fbfcfe')
    for i, im in enumerate(thumbs):
        im.thumbnail((840, 480))
        combined.paste(im, ((i % 2) * 840, (i // 2) * 480))
    combined.save(out / 'secuencia_integracion.png')
    return paths
