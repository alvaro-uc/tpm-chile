# Integración de indicadores por decisión de TPM

El notebook `notebooks/04_data_unificada.ipynb` importa las ocho series locales,
describe unidades y frecuencias, muestra vistas previas individuales y construye
una tabla de vínculos y una tabla ancha de las 161 decisiones. Incluye cuatro
láminas reproducibles: serie diaria y reuniones; período IPC frente a publicación;
relación por IDs y fila del modelo; ventana 2010–2025. Se guardan como PNG en
`docs/figures/integracion/`, con vista conjunta `secuencia_integracion.png`.
Se regeneran desde `src/processing/figuras_integracion.py`. La lógica está en
`src/processing/data_unificada.py`. No descarga datos ni presupone fechas de
publicación ausentes. Ejecutar desde un kernel limpio del entorno del proyecto.

## Relación entre tablas

- `id_reunion`: `RPM_AAAAMMDD`, derivado de la fecha del anuncio, estable frente a inserciones.
- `id_observacion`: variable y fecha original de la observación.
- Vínculo único por `(id_reunion, variable)`: permite reutilizar una medición en varias reuniones.
- Una observación puede tener varias versiones identificadas por su fecha de disponibilidad.

No conviene escribir un único número de reunión en cada observación original:
una publicación mensual puede corresponder a varias decisiones. La tabla larga
resuelve esa relación; la tabla ancha se obtiene pivotando sus valores.

## Disponibilidad y revisiones

Se conserva el corte operativo de reuniones, contrastado con la última fecha
presente en TPM diaria anterior al anuncio. Falta certificarlo con un calendario
bancario independiente. Toda selección respaldada exige publicación disponible
al cierre de ese día local. Se elige el período más reciente y su última versión
conocida al corte. No se interpola ni se desplazan filas para simular rezagos.

Las fechas de anuncio de TPM ya están documentadas. Los CSV de indicadores
solo contenían fecha de referencia y valor retrospectivo: faltaba agregar sus
fechas de publicación. El ejemplo real ya incorpora cuatro boletines del INE,
de julio a octubre de 2024, con fecha y valor de la página 1. La reunión del
17/10/2024, con corte 16/10, usa IPC de septiembre (0,1%, publicado 08/10) y
excluye octubre (1,0%, publicado 08/11). La del 03/09 usa julio, pues agosto
se publicó después de su corte. No se extrapolan fechas inferidas.

La cobertura se declara expresamente entre 08/08 y 08/11/2024 para IPC mensual;
fuera de ella no se arrastra el ejemplo hacia años posteriores. Las otras
variables y períodos quedan pendientes. El ejemplo documentado no completa
la reconstrucción histórica de las ocho series.

## Ventana de trabajo

Las decisiones y las vistas principales se recortan a 2010–2025. Se conserva
2009 como reserva técnica por separado para publicaciones de períodos previos
que puedan hacer falta al comienzo de 2010. No agrega filas de entrenamiento.
Se excluyen décadas anteriores y datos de 2026 en las copias de trabajo; los
archivos originales y los CSV limpios anteriores permanecen intactos.

La captura editable `data/processed/unificada/publicaciones_por_documentar.csv`
incluye las observaciones de 2010–2025 y la reserva de 2009. Completar fecha efectiva local, valor
publicado, fuente y localizador de la versión histórica. Una fecha de primera
publicación no autoriza utilizar el valor revisado descargado en 2026.
Para revisiones, añadir filas con el mismo ID y otra fecha. Con evidencia parcial,
el algoritmo solo conoce ese subconjunto; revisar exhaustividad antes de entrenar.
Preserva lo documentado en una captura existente y retira solo las filas vacías
fuera de la ventana. Incorpora los cuatro extractos donde aún no haya evidencia.
Las fuentes conservadas están en `data/raw/publicaciones_indicadores/`.

El IPC anual local corresponde a diciembre de cada año aunque se codifique en
enero: no representa inflación interanual mensual. El IMACEC es un índice
empalmado sujeto a revisiones. El desempleo comienza en marzo de 2010 y describe
trimestres móviles. La TPM diaria es una de las ocho entradas, redundante con
la TPM previa ya calculada; evaluar luego la pertinencia de cada predictor.
Las fuentes y referencias metodológicas están enlazadas dentro del notebook.

## Salidas locales

En `data/processed/unificada/` se generan `vinculos_reunion_variable.csv`,
`tpm_indicadores_disponibles.csv`, ocho `asignacion_<variable>.csv`, inventario
y cobertura. También se exportan ocho `serie_*_2010_2025.csv` y antecedentes
separados `antecedentes_2009_*.csv`. Se versiona la captura editable; las salidas grandes se regeneran
y permanecen ignoradas por Git. No se modifican los datasets originales.

`lista_para_modelo` exige ocho columnas documentadas y cortes dentro de la
cobertura de publicaciones registrada. No resuelve el calendario bancario. IDs, cobertura,
fechas, resultado posterior y variación no son predictores automáticos. Antes
de entrenar se deben revisar calendarios, publicaciones, versiones y antigüedad,
seleccionar variables y separar cronológicamente entrenamiento/prueba. La reunión
extraordinaria de marzo de 2020 permanece identificada para evaluación aparte.

Pruebas: `python -m unittest discover -s tests`. Los casos de integración
verifican exclusión de publicaciones posteriores y revisiones futuras, admisión
de publicaciones del día de corte, reutilización de observaciones y rechazo
de evidencias incompletas o versiones ambiguas.
