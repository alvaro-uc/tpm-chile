# Bitácora del avance del proyecto de TPM

**Entrega 2 · Video de avance · IMT2200 · Grupo 9**  
**Estado revisado al 16 de octubre de 2026 · Commit de referencia a5a32f9**  
**Equipo:** Loreto Cornejo, Fernando Osses, Macarena Perez y Álvaro Recabarren.

Esta bitácora reúne lo realizado desde la propuesta: recopilación de fuentes, limpieza, construcción del historial de decisiones y definición del experimento temporal. Sirve para estudiar el avance y preparar el video. La revisión comprende los diez commits del repositorio hasta `a5a32f9`, los tres notebooks, las tablas locales y la retroalimentación del profesor. [1–4]

**Resultado del avance:** contamos con ocho series originales del Banco Central, sus ocho CSV de limpieza, una tabla de 161 decisiones y una serie de cobre elegida de Cochilco con 4.042 cotizaciones. Está acordado predecir la dirección de la decisión al cierre del día hábil anterior. Todavía falta construir la base integrada con información efectivamente publicada antes de cada corte; no se han entrenado ni evaluado modelos.

## 1 Problemática y pregunta de análisis

La TPM forma parte de las condiciones financieras que enfrentan hogares y empresas. Antes de sus decisiones existe información pública sobre precios, actividad, empleo y condiciones externas. El proyecto estudia si esa información permite anticipar la dirección de la siguiente decisión monetaria. La motivación procede de la propuesta; todavía falta completar las referencias económicas y la literatura previa solicitadas por el profesor. [1, pp. 3–4; 2, p. 2]

**Pregunta principal:** ¿hasta qué punto los indicadores macroeconómicos públicos conocidos al cierre del día hábil anterior permiten anticipar si la próxima decisión de TPM será subir, mantener o bajar?

La tarea es una **clasificación de tres categorías**. El nivel exacto de la tasa y la magnitud del cambio no son el objetivo principal. La unidad de observación será una decisión de TPM. El período de estudio se mantiene en **2010–2025**; las observaciones de 2026 presentes en algunos originales quedan fuera del análisis principal.

Las preguntas secundarias todavía por responder son cuánto se mejora respecto de una línea base, qué ocurre con las clases menos frecuentes y si añadir expectativas aporta información adicional. La regresión logística multiclase es el modelo previsto y un árbol de decisión es una alternativa, sujetos al alcance del curso. Son planes, no resultados obtenidos. [1, pp. 5–6; 2, p. 3]

## 2 Qué exige el video

La consigna compartida solicita **el video**, con duración máxima de seis minutos, e incluye problemática, preguntas de análisis, descripción de datos y análisis realizados. El documento y el guion son materiales de preparación; no sustituyen ese entregable.

El plan de ensayo toma como referencia **domingo 18 de octubre de 2026 a las 23:59**. El texto compartido también menciona viernes 16; confirmar en la plataforma la fecha vigente antes de enviar. No se verificó una publicación del curso por otra vía.

La corrección del profesor identifica el curso como **IMT2200**. La propuesta y algunos archivos conservan IMT2210 o IMT210; para el video se usa la denominación corregida. [2, p. 4]

<!-- pagina -->

## 3 Inventario y función de los datos

Las fuentes BCCh son Excel con hojas de datos, metadatos e identificadores de serie. La limpieza produce CSV de fecha y valor. Cochilco entrega HTML con extensión `.xls`; su lector es específico. Los originales se conservan separados de las tablas derivadas. [3–6]

| Variable | Fuente y frecuencia | Qué contiene y cómo se usará |
|---|---|---|
| TPM | BCCh, diaria | Porcentaje. Construye la etiqueta; el nivel previo es candidato a predictor. |
| Fechas de decisión | Documentos BCCh, por reunión | 161 decisiones de 2010–2025. Definen las filas del futuro conjunto de análisis. |
| IPC mensual | INE vía BDE, mensual | Variación mensual en porcentaje. Candidato para representar presiones de precios. |
| IPC anual histórico | INE vía BDE, anual | Observaciones anuales. Se conserva como referencia; no es una serie mensual de inflación a doce meses. |
| IMACEC | BCCh, mensual | Índice empalmado original, referencia 2018=100. Aún no se ha elegido una transformación definitiva. |
| Desempleo | Serie INE vía BDE, mensual | Tasa total no ajustada en porcentaje. El archivo comienza en marzo de 2010. |
| Dólar observado | BCCh, diaria | Pesos chilenos por dólar. Candidato para condiciones externas y financieras. |
| Cobre elegido | Cochilco, diaria | Precio spot BML/LME en USD/libra. 4.042 observaciones, 04-01-2010 a 31-12-2025. |
| Expectativas TPM | EEE del BCCh, mensual | Mediana de la expectativa de TPM en el mes. Su papel en el modelo o benchmark sigue por decidir. |

La tabla principal de cobre es `data/processed/cobre_cochilco_diario_2010_2025.csv`. El archivo de reuniones actualmente versionado es `data/processed/reuniones_tpm_2010_2025_clean.csv`. Los restantes ocho archivos terminados en `_clean.csv` proceden del notebook 01. El antiguo `cu_usd_lb_clean.csv` corresponde al BCCh y queda como referencia, no como entrada elegida de cobre.

**Distinción de tamaños:** las 4.042 cotizaciones de cobre y las miles de filas diarias de TPM no son miles de ejemplos de entrenamiento. El historial tiene 161 decisiones; la muestra utilizable podrá ser menor por cobertura, rezagos y tratamiento de reuniones extraordinarias.

La revisión de esta bitácora comparó los valores numéricos de los ocho CSV con sus Excel originales: se conservaron sus filas y valores, con diferencia máxima de cero y sin valores numéricos nulos. Esto acredita fidelidad de extracción en las copias actuales. No certifica que ya estén resueltas la publicación histórica, las revisiones o la selección económica de cada variable.

El desempleo carece del inicio de 2010 en la copia disponible. Para inflación interanual mensual se necesitaría elegir una serie adecuada o justificar su cálculo con una historia compatible. No se debe presentar el IPC anual histórico como sustituto directo.

<!-- pagina -->

## 4 Decisiones metodológicas adoptadas

### Una fila por decisión y tres resultados posibles

La serie diaria de TPM permite reconocer cambios de tasa, pero no identifica por sí sola las reuniones que mantuvieron la tasa. Se recopilaron fechas oficiales y se construyó una tabla separada. Contar cada día sin cambio como una decisión de mantención habría creado una muestra equivocada. [4]

Para etiquetar se compara la TPM en el corte previo con la primera observación diaria estrictamente posterior al anuncio. La variación en puntos base es `(TPM posterior − TPM previa) × 100`. Un resultado positivo se etiqueta `sube`; cero, `mantiene`; negativo, `baja`. Es una regla operacional contrastada con los cambios de la serie, no una afirmación sobre la vigencia legal exacta de cada anuncio.

### Corte al cierre del día hábil anterior

Se acordó usar el cierre del día hábil anterior a la fecha de decisión, en `America/Santiago`. El calendario operativo toma las fechas observadas en el Excel diario oficial de TPM y elige la última estrictamente anterior a la decisión. Antes del modelo falta contrastarlo con un calendario bancario independiente. No se inventó una hora de publicación.

En reuniones de dos días, la fecha objetivo es el último día, cuando se anuncia el resultado. Por ello el corte puede coincidir con el primer día de la reunión; no significa predecir antes de su inicio.

| Ejemplo | Corte | TPM previa | TPM posterior | Etiqueta |
|---|---|---:|---:|---|
| 14-01-2010 | 13-01-2010 | 0,50 % | 0,50 % | Mantiene |
| 15-06-2010 | 14-06-2010 | 0,50 % | 1,00 % | Sube |
| 19-12-2023 | 18-12-2023 | 9,00 % | 8,25 % | Baja |

**Regla de integración pendiente:** elegir para cada indicador la última observación cuya publicación efectiva sea anterior o igual al corte. El mes al que se refiere un dato no equivale a la fecha en que se conoció. Por ejemplo, no corresponde utilizar el IMACEC de un mes antes de su publicación ni el promedio completo de cobre de un mes todavía abierto.

La TPM posterior, la variación y la etiqueta son resultados y deben excluirse de los predictores. La fecha de decisión identifica la fila; su uso como variable de calendario requeriría justificación aparte.

### Información revisada y reuniones extraordinarias

Las descargas actuales pueden contener revisiones desconocidas en su fecha original. Esto debe tratarse o declararse explícitamente, especialmente en indicadores de actividad. La regla de corte está acordada, pero por sí sola no elimina esa fuga de información.

Se conserva y marca la reunión extraordinaria del 16-03-2020. Su fecha se conoce retrospectivamente; falta decidir si el experimento principal abarcará solo reuniones programadas y cómo se evaluará ese episodio. La separación entrenamiento/prueba será cronológica; aún no se ha elegido el corte ni las ventanas.

<!-- pagina -->

## 5 Resultados descriptivos y controles realizados

### Historial de decisiones

| Decisión | Cantidad | Proporción del historial |
|---|---:|---:|
| Mantiene | 103 | 63,98 % |
| Baja | 31 | 19,25 % |
| Sube | 27 | 16,77 % |
| Total | 161 | 100 % |

Hay doce reuniones por año en 2010–2017, ocho en 2018–2025 salvo 2020, con nueve por la extraordinaria. Se reconciliaron los 58 cambios diarios con las 58 decisiones de subida o bajada. Hay 48 niveles contrastados adicionalmente con documentos; los otros 113 se derivan de la serie diaria. No se afirma haber leído individualmente los 161 comunicados. [4]

Se corrigió la fecha de diciembre de 2023: el archivo mostraba el día 20, pero el comunicado y la minuta respaldan el 19. Se incorporó diciembre de 2025 pese a aparecer bajo otro filtro de año. El salto marzo–junio de la primera muestra era una selección ilustrativa: abril y mayo de 2010 sí tuvieron reuniones de mantención.

La distribución muestra que mantener domina el historial. Una regla que predijera siempre esa clase acertaría descriptivamente 103 de 161 casos en el historial completo. **Ese 63,98 % no es una evaluación fuera de muestra ni el resultado de un modelo entrenado.** La futura línea base debe definirse con los datos de entrenamiento.

### Elección de Cochilco para todo el período

El Excel diario de cobre BCCh comienza el 05-10-2012, consistente con la primera observación de su serie. No se confirmó una omisión del usuario al descargar. Cochilco permitió recuperar el inicio de 2010 y luego completar todo el horizonte. Se decidió usar exclusivamente su precio contado/spot BML/LME. [5–6]

En 299 fechas comunes de 2012–2013, solo 39 valores coincidían dentro de ±0,005 USD/libra. La diferencia absoluta media era 0,03382469 y la máxima 0,2102 USD/libra. El 15-04-2013, BCCh registra 3,44 y Cochilco 3,2298. Esta diferencia no se explica solo por redondeo; su causa exacta no está demostrada. No se aumentó la tolerancia para forzar equivalencia ni se mezclaron las fuentes.

La serie elegida reúne tres descargas originales: 2010–2013, 2013–2019 y 2019–2025. Los 506 registros repetidos en sus solapamientos coinciden y se conservaron una sola vez. Hay datos en los 192 meses, sin fechas duplicadas ni precios nulos. Se convirtió centavos/libra a USD/libra dividiendo por 100.

Se conservan 132 días de lunes a viernes sin observación en un archivo auxiliar para revisar calendarios; incluyen cierres y feriados posibles, no 132 errores demostrados. No se interpolan ni rellenan fechas. Los recuentos mensuales y anuales no equivalen a certificar individualmente cada festivo de Londres.

Los 13 tests del repositorio pasaron en la revisión. Cubren controles de reuniones y cobre; no constituyen una auditoría económica integral de todos los indicadores. Todavía no hay EDA multivariable sobre la base temporal integrada, coeficientes estimados ni métricas predictivas.

<!-- pagina -->

## 6 Cronología respaldada por commits

Los nombres indican autoría registrada en Git, no una asignación exhaustiva de todo el trabajo del equipo. La integración a `main` fue por avance directo y no creó commits adicionales de merge.

| Fecha | Commit y autor | Avance verificable |
|---|---|---|
| 22-09-2026 | fa37977 · Álvaro | Estructura inicial, propuesta, README y requisitos. |
| 22-09-2026 | f4275ff · Álvaro | Incorporación de la serie diaria de TPM. |
| 23-09-2026 | c6784d7 · Álvaro | Otras siete series originales y retroalimentación del profesor. |
| 16-10-2026 | 8dfad65 · Fernando | Notebook inicial de limpieza y procesamiento. |
| 16-10-2026 | 6d80706 · Fernando | Actualización de dependencias. |
| 16-10-2026 | 2a6a244 · Fernando | Ocho CSV procesados y notebook de limpieza. |
| 16-10-2026 | 4f99f18 · Fernando | Corrección del notebook y del primer CSV. |
| 16-10-2026 | 23e716c · Álvaro | Fuentes, tabla y notebook de reuniones; regla temporal y tests. |
| 16-10-2026 | 2567871 · Fernando | Renombrado del CSV de reuniones con sufijo `_clean`. |
| 16-10-2026 | a5a32f9 · Álvaro | Cochilco 2010–2025, procedencia, tablas, notebook, controles y decisión de fuente. |

La primera limpieza tuvo una interpretación errónea de columnas; la versión actual identifica explícitamente fecha y valor. La comparación realizada para esta bitácora confirma la conservación numérica de los ocho archivos actuales. No hace falta presentar el error inicial como si siguiera vigente.

**Detalle de reproducibilidad por resolver:** el CSV versionado de reuniones termina en `_clean.csv`, pero el módulo y el notebook 02 conservan como salida `reuniones_tpm_2010_2025.csv`. El commit del cambio de nombre fue un renombrado sin cambio de contenido. Debe unificarse la convención antes de la siguiente integración; en esta revisión se leyó el archivo existente y se reconstruyó la tabla en memoria, sin alterar los datasets.

## 7 Respuesta a los comentarios del profesor

| Observación de la propuesta | Avance y estado actual |
|---|---|
| Definir qué significa anticipar | Acordado: cierre del día hábil anterior al anuncio. |
| Verificar cantidad y clases de decisiones | Resuelto para el historial: 161, distribuidas en 103/31/27. |
| Alinear publicación y revisiones | Pendiente por indicador; calendario operativo construido. |
| Aclarar papel de EEE | Serie disponible; experimento con/sin EEE o benchmark aún por definir. |
| Evaluar más allá de accuracy | Planificar matriz de confusión, métricas por clase y medida equilibrada; sin evaluación ejecutada. |
| Definir responsabilidades e hitos | Se propone reparto para el video; no hay asignación completa aprobada para modelamiento. |

No se presenta la preparación como evidencia de capacidad predictiva. Su aporte es que el experimento tiene una unidad de observación definida, fuentes documentadas y controles comprobables. [2, pp. 2–5]

<!-- pagina -->

## 8 Próximas tareas y preparación de la entrega

Antes de modelar: unificar el nombre de la tabla de reuniones; precisar publicación y revisiones de IPC, IMACEC, desempleo, dólar, cobre y EEE; resolver el inicio de desempleo; construir el cruce por disponibilidad al corte; definir transformaciones y rezagos; fijar tratamiento de extraordinarias y EEE; elegir validación cronológica, líneas base y métricas por clase. El escalamiento y selección de variables deberán ajustarse usando solo entrenamiento.

Para el video se propone este reparto, **pendiente de acuerdo del grupo**, sin atribuir tareas pasadas que Git no acredita:

| Integrante | Bloque del video | Material para preparar |
|---|---|---|
| Loreto | Problemática y pregunta | Objetivo de clasificación y período 2010–2025. |
| Fernando | Datos y limpieza | Inventario, notebook 01 y un ejemplo de fecha y valor. |
| Macarena | Reuniones y corte temporal | Distribución 103/31/27 y ejemplo de corte anterior. |
| Álvaro | Cobre y próximos pasos | Serie elegida, comparación de fuentes y límites del avance. |

**Sábado 17:** leer esta bitácora, acordar bloques, preparar cuatro vistas y ensayar con cronómetro; grabar tomas breves. **Domingo 18:** editar, revisar audio y cifras, comprobar duración y subir con margen antes de las 23:59, sujeto a confirmar la fecha oficial. Es una planificación propuesta, no un registro de tareas ya ejecutadas.

El [guion de ensayo](guion_video_avance_entrega_2.md) propone una narración breve y un objetivo de 5:30–5:45. Al mostrar código no conviene leerlo en voz alta: explicar qué transforma y qué valida. No afirmar que hay un predictor final, que todas las revisiones están resueltas o que se demostró qué fuente de cobre es incorrecta.

<!-- pagina -->

## 9 Evidencias y reproducción

1. **Propuesta proyecto IMT210.pdf**, páginas 3–6: problemática, pregunta, variables y diseño tentativo. El nombre original del archivo se conserva.
2. **docs/retroalimentacion_profesor.pdf**, páginas 1–5: observaciones sobre publicación, tamaño de muestra, EEE, evaluación y planificación; página 4: corrección a IMT2200.
3. **docs/README.md**, **notebooks/01_limpieza_y_procesamiento.ipynb** y los ocho Excel/CSV: definiciones, cobertura y extracción. La comparación numérica de esta revisión no ejecutó el notebook ni sobrescribió sus salidas.
4. **docs/reuniones_tpm.md**, **src/processing/reuniones_tpm.py**, **notebooks/02_reuniones_tpm.ipynb** y **data/raw/reuniones_tpm/**: reglas, fuentes y controles de las 161 decisiones.
5. **docs/cobre_historico.md** y **docs/cobre_validacion.json**: investigación de cobertura y comparación BCCh/Cochilco.
6. **docs/cobre_cochilco_validacion.json**, **src/processing/cobre_cochilco.py**, **notebooks/03_cobre_historico.ipynb** y **data/raw/cobre_historico/**: serie elegida y procedencia.
7. Historial de Git hasta **a5a32f9**: [repositorio del proyecto](https://github.com/alvaro-uc/tpm-chile) y [avance del cobre](https://github.com/alvaro-uc/tpm-chile/commit/a5a32f9c22f48c04fda893628fa1d1f4ced2f074).

Las descargas web fueron recopilaciones puntuales autorizadas. La transformación de reuniones y cobre se reproduce con archivos locales. Desde la raíz del repositorio y el entorno del proyecto:

```powershell
python -m src.processing.cobre_cochilco
python -m unittest discover -s tests
```

Para reuniones, `python -m src.processing.reuniones_tpm` genera actualmente el nombre sin `_clean`; tener presente la diferencia de convención registrada arriba. Para estudiar el proceso sin regenerar archivos puede leerse el notebook ejecutado.

La comprobación de esta bitácora reconstruyó 161 decisiones con sus clases y contrastes, verificó los ocho CSV contra sus valores originales y volvió a ejecutar los 13 tests. Los límites pendientes forman parte del avance comunicado y orientan la siguiente etapa.
