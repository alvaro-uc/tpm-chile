# Reuniones y decisiones de TPM, 2010–2025

Se conserva una tabla **aparte**, con una fila por decisión. No se modifica
`data/raw/tpm_bcentral_diaria.xlsx`: esa serie tiene una fila por día observado
y no permite identificar por sí sola las reuniones que mantuvieron la tasa.
La futura tabla de indicadores se construirá sobre estas reuniones.

## Alcance y resultado de la recopilación

Consulta de fuentes: **16 de octubre de 2026**. Se recopilaron 161 decisiones:
103 mantenciones, 31 bajas y 27 subidas. Hay 12 reuniones por año en 2010–2017,
8 por año en 2018–2025, salvo 2020, con 9 al incluir la especial del 16 de marzo.
La reducción de 12 a 8 reuniones ordinarias rige desde 2018 según el
[Banco Central](https://www.bcentral.cl/es/web/banco-central/areas/politica-monetaria).
El tamaño final para entrenar podrá ser menor por cobertura de predictores y rezagos.

El salto de marzo a junio en la muestra inicial de revisión fue una selección
para mostrar una subida, no una ausencia de reuniones: en 2010 hubo reuniones
el **15 de abril** y **13 de mayo**, ambas de mantención en 0,50%.

## Fuentes conservadas y trazabilidad

- `data/raw/reuniones_tpm/rpm_boletines_2010_2012.json`: fecha y oración de decisión de 31
  boletines oficiales: todos los meses de 2010 y 2011 y enero–julio de 2012.
  Conserva URL, página del PDF, SHA256 y nivel anunciado. Son extractos de
  documentos, no una API ni una base original publicada por el BCCh.
- `data/raw/reuniones_tpm/rpm_fuentes_complementarias.json`: fechas de agosto–diciembre de
  2012 y de 2013–2014, con URLs de actas, minutas, registros del repositorio y
  memorias oficiales. Las actas sirven para identificar la fecha, **no como
  información predictora disponible antes de la reunión**.
- `data/raw/reuniones_tpm/rpm_memoria_2014.html`: copia sin modificar del Anexo I digital de
  la Memoria 2014, con sus doce comunicados. La lista de niveles se contrasta
  con esta copia además de la serie diaria.
- `data/raw/reuniones_tpm/rpm_archivo_2015_2025.json`: transcripción del texto visible en el
  [archivo oficial por año](https://www.bcentral.cl/es/areas/politica-monetaria/reunion-de-politica-monetaria-rpm/documentacion-rpm),
  consultado con su navegador y filtros. Se conserva el texto original de las
  fechas, incluso rangos, y una corrección documentada.

Los boletines completos descargados durante la recopilación son una caché
temporal fuera del repositorio. No se añade una dependencia PDF para ejecutar
el procesamiento: los extractos y las fechas ya quedan conservados localmente.
La recopilación puntual por web fue autorizada para este historial; la
regeneración del CSV es local y no hace peticiones de red.

El listado del archivo puso **20 de diciembre de 2023**, pero el
[comunicado](https://www.bcentral.cl/web/banco-central/contenido/-/detalle/comunicado-reunion-de-politica-monetaria-diciembre-2023)
y la minuta de la sesión N°302 indican **19 de diciembre**. Se conserva el
texto del listado y se aplica explícitamente esa corrección. No se deduce la
fecha de reunión restando automáticamente un día a cada cambio de TPM.

El filtro 2025 del sitio devolvió siete fechas; la del 16 de diciembre de 2025
aparecía en la tabla inicial de 2026. Se incorporó y se contrastó con su
[comunicado](https://www.bcentral.cl/contenido/-/detalle/prensa/comunicados-rpm/comunicado-rpm-diciembre-2025).
Esto impide dar por completa la extracción usando solo el selector de año.

## Corte de información acordado

La predicción se realiza **al cierre del día hábil anterior a la fecha de
decisión**, en la zona `America/Santiago`. Para una reunión de dos días,
`fecha_decision` es el último día, cuando se anuncia el resultado. Por tanto,
el corte puede coincidir con el primer día de la reunión: no equivale a
predecir antes de que esta comience.

En esta primera versión, el calendario de días hábiles se aproxima mediante
las **fechas presentes en el Excel diario oficial de TPM**. El corte es la
última fecha observada estrictamente anterior a la decisión; así se tienen
en cuenta fines de semana y feriados según esa serie. No se supone que todo
lunes–viernes sea hábil. Antes del modelamiento conviene contrastar este
calendario operativo con un calendario bancario independiente. La columna es
una fecha de corte, no una hora de mercado inventada.

Para cada indicador deberá cumplirse que su fecha efectiva de publicación
sea como máximo ese corte. La fecha del período que describe el dato no
sustituye su publicación. Los niveles posteriores y la etiqueta son datos
del resultado, y **no pueden entrar como predictores**. Los valores revisados
de indicadores históricos requerirán un tratamiento o limitación explícita.

La reunión extraordinaria del 16 de marzo de 2020 se conserva y se marca.
Su fecha se conoce retrospectivamente: no asumir que un observador sabía
el día anterior que se convocaría. Antes de evaluar un modelo habrá que
definir si el experimento principal incluye solo reuniones programadas y
usar las extraordinarias como evaluación separada. No se elimina ahora.

## Tabla producida

El notebook `notebooks/02_reuniones_tpm.ipynb` presenta el proceso paso a paso:
inventario y lectura de fuentes, normalización y correcciones, lectura de TPM
diaria, alineación temporal, creación de etiquetas, validaciones y exportación.
Se ejecuta desde un kernel limpio usando solo los insumos locales; reproduce
la transformación, no la recopilación web original. Las fuentes están agrupadas
en `data/raw/reuniones_tpm/` y la tabla derivada permanece en `data/processed/`.

`data/processed/reuniones_tpm_2010_2025.csv`, regenerable con:

```powershell
.venv\Scripts\python.exe -m src.processing.reuniones_tpm
```

| Columna | Significado / uso |
|---|---|
| `fecha_decision` | Fecha oficial del anuncio; identificador temporal de la fila. |
| `fecha_texto_fuente` | Texto conservado de la fuente o fecha transcrita de ella. |
| `fuente_fecha_url` | Fuente oficial que respalda la fecha; puede contener varias reuniones. |
| `tpm_anunciada_verificada_pct` | Nivel contrastado documentalmente cuando se revisó el texto; vacío en los demás casos. |
| `tipo_reunion` | Ordinaria o extraordinaria según las fuentes consultadas. |
| `nota_fuente` | Página, localizador o corrección, cuando corresponde. |
| `fecha_corte` | Último día observado en TPM diaria antes de la decisión. |
| `tpm_previa_pct` | Nivel de TPM en el corte. Candidato a predictor. |
| `fecha_observacion_posterior` | Primera fecha de TPM diaria estrictamente posterior a la decisión; **no es necesariamente la fecha de anuncio ni una certificación de vigencia legal**. |
| `tpm_posterior_pct` | Nivel de TPM en esa observación posterior. Dato del resultado. |
| `variacion_pb` | `(tpm_posterior_pct - tpm_previa_pct) * 100`; 1 punto porcentual = 100 puntos base. |
| `decision` | `sube`, `mantiene` o `baja` según el signo de la variación. Etiqueta objetivo. |
| `contraste_tpm` | `coincide_con_documento` (48 niveles) o `derivada_de_serie_diaria` (113). |
| `regla_corte` | Regla acordada y zona horaria; no introduce hora de publicación supuesta. |
| `calendario_corte` | Identifica el calendario operativo usado. |

Todos los niveles usan unidades porcentuales: 0.5 significa 0,50%, no 50%.
**No se ha afirmado una lectura individual de los 161 comunicados:** las
fechas están respaldadas por fuentes oficiales; 48 niveles tienen contraste
documental adicional y 113 se obtienen de la serie diaria original.

## Comprobaciones realizadas

El procesamiento falla antes de escribir si encuentra fechas duplicadas,
datos no numéricos, falta de observación anterior/posterior, discrepancias
con los 48 niveles documentados o cambios diarios sin reunión asociada.
Se reconciliaron los **58 cambios diarios** del período con las 58 decisiones
de subida/bajada, con correspondencia única. Los 103 casos de mantención
proceden de fechas de reunión, no de considerar cada día sin cambio una reunión.

Ejemplos revisados:

| Decisión | Corte | TPM previa | Observación posterior | TPM posterior | Etiqueta |
|---|---|---:|---|---:|---|
| 2010-01-14 | 2010-01-13 | 0.50 | 2010-01-15 | 0.50 | mantiene |
| 2010-04-15 | 2010-04-14 | 0.50 | 2010-04-16 | 0.50 | mantiene |
| 2010-05-13 | 2010-05-12 | 0.50 | 2010-05-14 | 0.50 | mantiene |
| 2010-06-15 | 2010-06-14 | 0.50 | 2010-06-16 | 1.00 | sube |
| 2014-04-17 | 2014-04-16 | 4.00 | 2014-04-21 | 4.00 | mantiene |
| 2023-12-19 | 2023-12-18 | 9.00 | 2023-12-20 | 8.25 | baja |

La fila de abril de 2014 muestra por qué no basta sumar un día de calendario:
la siguiente observación es del lunes 21, después de Semana Santa.

Verificación local:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

La tabla no integra todavía IPC, IMACEC, desempleo, dólar, cobre ni EEE, y no
ejecuta ni modifica el notebook de limpieza del equipo.
