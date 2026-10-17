"""Regenera el notebook 04; luego ejecutarlo desde un kernel limpio."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

cells = []


def md(text):
    cells.append(dict(cell_type='markdown', metadata={}, source=text.splitlines(keepends=True)))


def code(text):
    cells.append(dict(cell_type='code', metadata={}, source=text.splitlines(keepends=True), execution_count=None, outputs=[]))


md('''# 04 · De las publicaciones a la tabla unificada de TPM

La muestra comprende **161 decisiones de 2010–2025**, con una fila por anuncio. Las fechas de anuncio de TPM **ya están documentadas**. Lo que los CSV de indicadores no informaban era cuándo se publicó cada resultado, distinto del mes que mide. Aquí incorporamos un caso real verificado de IPC y explicamos cómo extenderlo a las ocho series.

Primero mostramos la lógica visualmente; luego importamos, recortamos, exploramos e indexamos cada dataset. La ejecución es local y reproducible desde la raíz o `notebooks/`, con el entorno del proyecto. Los extractos de cuatro boletines INE y sus enlaces quedan conservados en `data/raw/publicaciones_indicadores/`.
''')
code('''from pathlib import Path
import sys
import pandas as pd
from IPython.display import display, Image

ROOT = Path.cwd().resolve()
if not (ROOT / 'src').is_dir():
    ROOT = ROOT.parent
assert (ROOT / 'src/processing/data_unificada.py').exists()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.processing.data_unificada import (
    SERIES, cargar, preparar_captura, vincular, exportar
)
from src.processing.figuras_integracion import generar_figuras
reuniones, datasets, inventario = cargar(ROOT)
pd.set_option('display.max_columns', 12)
''')
md('''## 1. Por qué necesitamos las fechas de anuncio

La TPM diaria registra un nivel que se repite mientras no cambie la tasa. Una reunión que mantiene la TPM no produce un salto: por eso **el tramo plano no permite identificar sus reuniones**. Una subida o baja tampoco convierte automáticamente su primera observación diaria en fecha de anuncio. El historial de comunicados identifica los eventos y la serie diaria permite contrastar niveles.
''')
code('''figuras = generar_figuras(ROOT, reuniones, datasets)
display(Image(filename=str(figuras[0])))
display(reuniones.loc[reuniones.fecha_decision.between('2010-04-01', '2010-06-30'),
    ['id_reunion', 'fecha_decision', 'fecha_corte', 'tpm_previa_pct', 'tpm_posterior_pct', 'decision']])
''')
md('''## 2. El día hábil anterior es el corte de información

Para la decisión del **17/10/2024**, el corte es el **16/10/2024** al cierre, en `America/Santiago`. El IPC de septiembre fue publicado el 08/10 y estaba disponible; el de octubre fue publicado el 08/11 y todavía no existía como información pública. Elegir el IPC del mismo mes de la reunión usando el archivo actual introduciría información futura.

El criterio es **última información publicada hasta el corte**, no que todas las mediciones tengan fecha del día anterior. En cobre puede ser una cotización diaria; en IPC, un resultado de un mes anterior. Los retrasos no son fallas del dataset: son parte de cómo la información llega a quien predice.

Fuentes verificadas: [INE, IPC septiembre (boletín 311)](https://www.ine.gob.cl/docs/default-source/%C3%ADndice-de-precios-al-consumidor/boletines/espa%C3%B1ol/2024/boletin_ipc_septiembre-2024.pdf), [INE, IPC octubre (boletín 312)](https://www.ine.gob.cl/docs/default-source/%C3%ADndice-de-precios-al-consumidor/boletines/espa%C3%B1ol/2024/boletin-ipc-octubre-2024.pdf), [BCCh, comunicado del 17/10/2024](https://www.bcentral.cl/contenido/-/details/comunicado-rpm-octubre-2024). Las otras dos fuentes del ejemplo se conservan en el CSV de extractos.
''')
code('''display(Image(filename=str(figuras[1])))
diaria = datasets['tpm_bcentral_diaria'][['fecha']].rename(columns={'fecha': 'corte_recalculado'})
control = pd.merge_asof(reuniones.sort_values('fecha_decision'), diaria,
    left_on='fecha_decision', right_on='corte_recalculado', direction='backward', allow_exact_matches=False)
assert control.fecha_corte.eq(control.corte_recalculado).all()
assert reuniones.id_reunion.is_unique
print('Calendario operativo reconciliado: última fecha TPM diaria estrictamente anterior al anuncio.')
''')
md('''El calendario operativo usa fechas presentes en la serie oficial, no una resta de un día ni un supuesto lunes–viernes. Falta contrastarlo con un calendario bancario independiente. Para reuniones de dos días, el corte puede coincidir con el primero: no significa predecir antes del inicio de la sesión. Los calendarios de mercado de cobre y de Chile pueden diferir.
''')
md('''## 3. Indexar y vincular las tablas

`id_reunion = RPM_AAAAMMDD` identifica el anuncio y permanece estable al insertar nuevas filas. `id_observacion = variable_AAAAMMDD` identifica el período medido. La tabla intermedia contiene **un vínculo por reunión y variable**; una medición puede servir a varias reuniones. Por eso no escribimos un único ID de reunión en cada fila original de un indicador.

Los IDs permiten rastrear la relación; la fecha de disponibilidad determina qué observación se elige. Después pivotamos los vínculos para obtener una fila por reunión y una columna por indicador. `decision` es la etiqueta que queremos predecir; se conoce después del corte y nunca entra en los predictores.
''')
code('''display(Image(filename=str(figuras[2])))
''')
md('''## 4. Recortar la ventana de trabajo

Las vistas principales y la muestra de reuniones quedan en **2010–2025**. Las copias analíticas no incluyen décadas anteriores ni datos posteriores a 2025. Conservamos **solo 2009 como reserva técnica separada**, porque algunas publicaciones disponibles en enero de 2010 describen períodos del año anterior; eliminarlo todo dejaría vacíos artificiales al inicio. La reserva no agrega decisiones de 2009 al entrenamiento. Se revisará su uso al completar los calendarios; no se rellenan faltantes con información futura.

Los archivos originales conservan su cobertura. Las salidas `serie_*_2010_2025.csv` sí quedan recortadas; `antecedentes_2009_*.csv` se exportan aparte.
''')
code('''display(Image(filename=str(figuras[3])))
display(inventario[['variable', 'inicio_original', 'fin_original', 'filas_2010_2025', 'antecedentes_2009']])
assert reuniones.fecha_decision.between('2010-01-01', '2025-12-31').all()
assert all(df.fecha.between('2009-01-01', '2025-12-31').all() for df in datasets.values())
''')
md('''## 5. Importación y exploración individual de las ocho series

Las vistas siguientes solo muestran 2010–2025. `fecha` es el campo original de referencia; no se renombra como publicación sin comprobarlo. Se usa exclusivamente **Cochilco** para cobre; no se añaden como variables las tablas auxiliares ni la alternativa BCCh.
''')
warnings = {
    'tpm_bcentral_diaria': 'Contrastar con TPM previa. El nivel anunciado, el posterior y la variación son datos del resultado y se excluyen de X.',
    'clp_usd': 'El dólar observado describe operaciones del día bancario previo a su publicación. Distinguir ambas fechas; no aplicar un segundo desfase automático.',
    'cu_usd_lb': 'Sin interpolación. Cuando el mercado no observa el día de corte, usar la última cotización anterior disponible e informar su antigüedad.',
    'desempleo_total_mensual': 'Son estimaciones de trimestres móviles actualizadas mensualmente. La serie comienza en marzo de 2010; las primeras reuniones carecen de esta entrada. Revisar mes final y recalibraciones.',
    'exp_tpm_mensual_mediana': 'La fecha al primer día del mes codifica el período; no prueba disponibilidad. Conservar el horizonte esperado y la fecha efectiva de cada encuesta.',
    'imacec_empalmado_original': 'Es un índice original empalmado, no crecimiento. Puede contener revisiones posteriores. La fecha inicial de publicación no autoriza usar el valor revisado de hoy. El calendario cambió en 2019.',
    'ipc_general_mensual': 'Es variación mensual, no nivel del índice. El mes de referencia y su publicación en el siguiente mes son distintos, como muestra el ejemplo real.',
    'ipc_general_anual': 'Es variación histórica anual de diciembre, codificada en enero; no inflación interanual mensual. Se importa por estar disponible, pero su pertinencia como predictor debe revisarse.',
}
from src.processing.data_unificada import SERIES
for var, filename, freq, unit, description in SERIES:
    md(f'### {var}\n\n{description}\n\nArchivo: `{filename}`. Frecuencia: {freq}. Unidad: {unit}.\n\n{warnings[var]}')
    code(f'''serie = datasets[{var!r}]
principal = serie.loc[serie.en_ventana_2010_2025]
display(principal.head(4))
print('Filas 2010–2025:', len(principal), '| Reserva 2009:', int((~serie.en_ventana_2010_2025).sum()),
      '| Duplicados:', serie.fecha.duplicated().sum(), '| Nulos:', serie[{var!r}].isna().sum())
''')
md('''## 6. Incorporar las fechas de publicación: ejemplo ya documentado

Aquí corregimos la falta de fechas de publicación **para el caso ilustrado**, usando cuatro boletines consecutivos: IPC de julio, agosto, septiembre y octubre de 2024. Los extractos conservan período, fecha efectiva, valor publicado, enlace y página. No hace falta que cada fila se documente a mano: se pueden capturar calendarios y boletines en bloque, siempre contrastando fuentes y versiones.

La captura editable se conserva al reejecutar; solo se eliminan filas vacías fuera de la ventana y se incorporan los ejemplos donde aún no hay evidencia. Para completar otras fechas, añadir `fecha_disponible`, `valor_publicado`, `fuente_publicacion` y `evidencia_version`. `valor_descargado` solo ayuda al contraste. Para revisiones, añadir versiones con el mismo ID y otra fecha.

**El ejemplo no completa aún las ocho series de 2010–2025.** La cobertura del calendario se declara en `cobertura_ejemplo.csv`: 08/08–08/11/2024 para IPC mensual. Fuera de ese intervalo se mantienen pendientes; no se arrastra la última publicación del ejemplo a todas las reuniones de 2025.
''')
code('''publicaciones, cobertura = preparar_captura(ROOT, datasets)
display(publicaciones.loc[publicaciones.fecha_disponible.notna()])
display(cobertura)
print('Registros de captura:', len(publicaciones))
''')
md('''## 7. Asignación por disponibilidad y revisión de vínculos

Se consideran publicaciones con `fecha_disponible <= fecha_corte`. Entre ellas se selecciona el período de referencia más reciente y su última versión disponible al corte. Una revisión tardía de un período antiguo no desplaza un período más reciente. No se usa el dato más cercano en ambas direcciones, desplazamientos de filas ni una unión exacta por mes.

`candidato_*` es la selección ingenua por fecha de referencia: permite ver el riesgo, pero **no es un predictor validado**. Los campos `valor` y `fecha_disponible` contienen la selección respaldada en el intervalo documentado. No se fija aún una tolerancia universal de antigüedad: se revisará por variable.
''')
code('''vinculos, unificada = vincular(reuniones, datasets, publicaciones, cobertura)
caso = vinculos.loc[vinculos.id_reunion.eq('RPM_20241017') & vinculos.variable.eq('ipc_general_mensual')]
display(caso[['id_reunion', 'fecha_corte', 'candidato_fecha', 'candidato_valor',
              'id_observacion', 'fecha_referencia', 'fecha_disponible', 'valor']])
assert caso.iloc[0].id_observacion == 'ipc_general_mensual_20240901'
assert float(caso.iloc[0].valor) == 0.1
assert float(caso.iloc[0].candidato_valor) == 1.0
print('Unión por referencia: octubre (1,0%). Unión por publicación: septiembre (0,1%).')
for variable, grupo in vinculos.groupby('variable', sort=False):
    print(variable)
    display(grupo[['id_reunion', 'fecha_corte', 'candidato_fecha', 'candidato_valor',
                   'fecha_disponible', 'valor', 'estado']].head(3))
''')
md('''## 8. Controles, cobertura y exportación

La tabla preserva las 161 decisiones. Los vacíos distinguen tareas de documentación pendientes de la disponibilidad real de los indicadores; no significan que nunca se publicaran. `lista_para_modelo` exige ocho valores y calendarios cubiertos; no reemplaza la auditoría de fuentes ni la selección de variables. IDs, fechas y campos del resultado no entran automáticamente al modelo.

La fecha de la reunión extraordinaria de marzo de 2020 se conoce retrospectivamente; decidir su evaluación separada antes de entrenar. Mantener una separación cronológica entrenamiento/prueba no elimina por sí sola una fuga causada por predictores publicados después del corte.
''')
code('''resumen = vinculos.groupby('variable', sort=False).agg(
    reuniones=('id_reunion', 'size'), candidatos=('candidato_id', 'count'),
    candidatos_exactos=('candidato_en_fecha_corte', 'sum'),
    valores_documentados=('valor', 'count'),
    maxima_antiguedad_dias=('dias_desde_publicacion', 'max'))
display(resumen)
assert len(vinculos) == len(reuniones) * len(SERIES)
assert not vinculos.duplicated(['id_reunion', 'variable']).any()
documentados = vinculos.loc[vinculos.valor.notna()]
assert documentados.fecha_disponible.le(documentados.fecha_corte).all()
assert documentados.calendario_documentado.all()
assert vinculos.fecha_corte.lt(vinculos.fecha_decision).all()
assert not {'tpm_posterior_pct', 'variacion_pb', 'tpm_anunciada_verificada_pct'} & set(unificada)
assert vinculos.loc[vinculos.fecha_corte.gt('2024-11-08'), 'valor'].isna().all()
comparacion = vinculos.loc[vinculos.variable.eq('tpm_bcentral_diaria')].merge(
    reuniones[['id_reunion', 'tpm_previa_pct']], on='id_reunion', validate='one_to_one')
assert comparacion.candidato_valor.eq(comparacion.tpm_previa_pct).all()
print('Controles temporales, cobertura, cardinalidad y TPM previa: OK')
''')
code('''vinculos, unificada = exportar(ROOT, reuniones, datasets, publicaciones, cobertura)
salida = ROOT / 'data/processed/unificada'
inventario.to_csv(salida / 'inventario_series.csv', index=False, date_format='%Y-%m-%d')
resumen.to_csv(salida / 'cobertura_por_variable.csv')
display(unificada.loc[unificada.id_reunion.eq('RPM_20241017')])
print('Reuniones:', len(unificada), '| Con ocho valores y calendarios documentados:', int(unificada.lista_para_modelo.sum()))
print('Salidas:', salida.relative_to(ROOT))
print('Series recortadas: serie_*_2010_2025.csv. Antecedentes separados: antecedentes_2009_*.csv.')
''')
md('''### Pendientes para completar la tabla del modelo

El mecanismo de integración y el caso real de IPC quedan comprobados. Sigue la reconstrucción de publicaciones para las ocho variables durante 2010–2025, incluyendo versiones históricas de series revisables. No basta aplicar a todo el período un calendario actual: por ejemplo, [BCCh anunció un cambio en la publicación del IMACEC en 2019](https://www.bcentral.cl/contenido/-/details/imacec-junio-2019-6). Las [versiones de calibración ENE](https://bancodatosene.ine.cl/) también requieren atención.

Al completar esa información se revisarán la pertinencia del IPC anual, la antigüedad admisible de cada indicador y el calendario bancario independiente. La tabla de entrenamiento usará los valores que se conocían en cada corte, aunque hoy exista información más reciente.
''')

for i, cell in enumerate(cells):
    cell['id'] = f'cell-{i:02d}'
notebook = dict(cells=cells, metadata={
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.12'}}, nbformat=4, nbformat_minor=5)
path = Path(__file__).with_name('04_data_unificada.ipynb')
path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding='utf-8')
print(path)
