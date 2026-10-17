# Guion para el video de avance del proyecto de TPM

**Entrega 2 · IMT2200 · Grupo 9 · Versión coordinada al 17-10-2026**

Presentación de **8 diapositivas**. Objetivo de ensayo: **5:40**. Margen hasta **6:00**. El texto hablado contiene **727 palabras**, equivalente a unas 128 por minuto si ocupa todo el tiempo. El ritmo real y los gestos deben ensayarse con cronómetro. Los tiempos incluyen el cambio de lámina. Las acotaciones y las fuentes no se leen en voz alta.

Este guion sigue la consigna descrita por el usuario: problemática, preguntas, descripción de datos, análisis realizados y avances, en un video de aproximadamente seis minutos. No constituye una revisión independiente de Canvas.

El reparto de voces es una propuesta. Cada persona presenta dos láminas consecutivas. Si graba una sola persona, conservar el orden y los tiempos.

| Lámina | Tiempo | Voz propuesta | Tema |
|---|---|---|---|
| 1 | 0:00-0:30 | Loreto | ¿Podemos anticipar al Banco Central? |
| 2 | 0:30-1:10 | Loreto | Datos para cada decisión |
| 3 | 1:10-1:55 | Fernando | Las mantenciones concentran el 64% de las decisiones |
| 4 | 1:55-2:35 | Fernando | Trayectoria de la TPM entre 2010 y 2025 |
| 5 | 2:35-3:15 | Macarena | Las mantenciones quedan dentro de un tramo plano |
| 6 | 3:15-4:10 | Macarena | La publicación determina qué IPC estaba disponible |
| 7 | 4:10-4:55 | Álvaro | Una fila por reunión, con vínculos trazables |
| 8 | 4:55-5:40 | Álvaro | Avance actual y próxima evaluación |

## Diapositiva 1: ¿Podemos anticipar al Banco Central?

**0:00-0:30 · Loreto · 30 segundos**

**Texto hablado**

Nuestro proyecto estudia cuánto permiten anticipar los indicadores macroeconómicos públicos la próxima decisión de Tasa de Política Monetaria del Banco Central de Chile. Queremos clasificar si la tasa sube, se mantiene o baja, porque esas decisiones influyen en las condiciones de crédito, ahorro e inversión. Trabajamos con el período de 2010 a 2025.

**Puntero y pantalla**

Señalar las tres clases en orden. Detenerse en el período 2010–2025. No leer los nombres del equipo.

**Fuentes**

- README.md
- docs/bitacora_avance_entrega_2.md: pregunta de análisis y estado del proyecto

## Diapositiva 2: Datos para cada decisión

**0:30-1:10 · Loreto · 40 segundos**

**Texto hablado**

Reunimos ocho series de datos: TPM previa, dólar observado, cobre, desempleo, expectativas de TPM, IMACEC y dos archivos de IPC. Combinan frecuencias diarias, mensuales y anuales. Conservamos los originales y generamos copias analíticas de 2010 a 2025, con antecedentes de 2009 separados para las primeras decisiones. Para el cobre elegimos exclusivamente Cochilco, con cuatro mil cuarenta y dos cotizaciones. También detectamos una distinción importante: el IPC anual histórico corresponde a diciembre, por lo que su pertinencia como predictor aún está en revisión.

**Puntero y pantalla**

Recorrer la columna de frecuencias. Señalar cobre Cochilco y luego IPC anual. Cerrar indicando la ventana de análisis.

**Fuentes**

- docs/README.md: inventario de series
- data/processed/cobre_cochilco_diario_2010_2025.csv
- src/processing/data_unificada.py: SERIES y ventana analítica

## Diapositiva 3: Las mantenciones concentran el 64% de las decisiones

**1:10-1:55 · Fernando · 45 segundos**

**Texto hablado**

El historial reúne ciento sesenta y una decisiones: ciento tres mantenciones, treinta y una bajas y veintisiete subidas. La mantención representa aproximadamente el sesenta y cuatro por ciento. Este es un primer resultado del análisis: las clases están desbalanceadas. Un clasificador que siempre dijera mantener alcanzaría ese porcentaje sobre el registro completo. Esa cifra describe la muestra y no es un resultado fuera de muestra. Más adelante debemos calcular una línea base en la partición temporal correspondiente y evaluar cada clase, para comprobar si el modelo reconoce también subidas y bajas.

**Puntero y pantalla**

Rodear 103 y después señalar 31 y 27. Detenerse en 64%. No presentar este porcentaje como rendimiento de un modelo entrenado.

**Fuentes**

- data/processed/reuniones_tpm_2010_2025_clean.csv: decision
- Cálculos: 103/161 = 63,98%; 31/161 = 19,25%; 27/161 = 16,77%

## Diapositiva 4: Trayectoria de la TPM entre 2010 y 2025

**1:55-2:35 · Fernando · 40 segundos**

**Texto hablado**

La trayectoria permite ubicar las decisiones en el tiempo. La línea muestra el nivel de la TPM diaria y los marcadores señalan los anuncios de subidas y bajas. Observamos períodos de estabilidad, un nivel de medio punto durante parte de 2020 y 2021, y un máximo de once coma veinticinco por ciento durante 2022 y 2023. Este gráfico describe la evolución, pero por sí solo no explica las causas de cada decisión. También recuerda por qué la evaluación tendrá que respetar el orden temporal: los distintos períodos no representan contextos idénticos.

**Puntero y pantalla**

Seguir la línea de izquierda a derecha. Señalar la zona baja de 2020–2021 y la meseta de 2022–2023. Identificar ambos símbolos en la leyenda.

**Fuentes**

- data/processed/tpm_bcentral_diaria_clean.csv: ventana 2010–2025
- data/processed/reuniones_tpm_2010_2025_clean.csv: fechas y decisiones
- Los marcadores usan la fecha de anuncio y el nivel posterior contrastado, no certifican fecha de vigencia legal

## Diapositiva 5: Las mantenciones quedan dentro de un tramo plano

**2:35-3:15 · Macarena · 40 segundos**

**Texto hablado**

Este acercamiento muestra por qué necesitamos una tabla de reuniones. En abril y mayo de 2010 hubo decisiones que mantuvieron la tasa en cero coma cinco por ciento. La serie diaria permanece plana y no identifica esos anuncios. En junio aparece otra distinción: la subida se anuncia el día quince, mientras la primera observación diaria con el nuevo nivel corresponde al dieciséis. Por eso usamos las fechas oficiales de anuncio para definir los eventos, y la serie diaria para contrastar sus niveles y construir la etiqueta.

**Puntero y pantalla**

Rodear los dos marcadores de mantención sin dibujar sobre las etiquetas. Señalar después el anuncio del 15/06 y el salto del 16/06.

**Fuentes**

- docs/reuniones_tpm.md: casos 15/04, 13/05 y 15/06 de 2010
- data/processed/reuniones_tpm_2010_2025_clean.csv
- data/processed/tpm_bcentral_diaria_clean.csv

## Diapositiva 6: La publicación determina qué IPC estaba disponible

**3:15-4:10 · Macarena · 55 segundos**

**Texto hablado**

Para anticipar cada decisión fijamos el corte al cierre del día hábil anterior. La decisión del diecisiete de octubre de 2024 tiene corte el dieciséis. El IPC de septiembre se publicó el ocho de octubre, con una variación mensual de cero coma uno por ciento, y ya estaba disponible. El IPC de octubre se publicó recién el ocho de noviembre. Aunque hoy figure en el archivo descargado, usarlo para esa reunión introduciría información futura. Entonces no exigimos que todas las variables se midan el día anterior: exigimos que estuvieran publicadas hasta ese corte. Para variables mensuales puede corresponder el mes previo, o incluso uno más antiguo. Ya verificamos cuatro boletines consecutivos del IPC para demostrar este mecanismo.

**Puntero y pantalla**

Seguir la barra de septiembre hasta su publicación del 08/10. Señalar el corte 16/10. Luego señalar 08/11 al otro lado del corte y marcarlo como excluido.

**Fuentes**

- data/raw/publicaciones_indicadores/ipc_ejemplo_2024.csv
- https://www.ine.gob.cl/docs/default-source/%C3%ADndice-de-precios-al-consumidor/boletines/espa%C3%B1ol/2024/boletin_ipc_septiembre-2024.pdf
- https://www.ine.gob.cl/docs/default-source/%C3%ADndice-de-precios-al-consumidor/boletines/espa%C3%B1ol/2024/boletin-ipc-octubre-2024.pdf
- https://www.bcentral.cl/contenido/-/details/comunicado-rpm-octubre-2024

## Diapositiva 7: Una fila por reunión, con vínculos trazables

**4:10-4:55 · Álvaro · 45 segundos**

**Texto hablado**

La integración usa un identificador estable para la reunión y otro para cada observación. Una tabla intermedia guarda qué medición corresponde a cada reunión y variable, junto con su fecha de publicación y fuente. El criterio temporal decide qué dato entra. En este ejemplo, la reunión de octubre se vincula con el IPC de septiembre. Una misma medición puede servir para varias reuniones si sigue siendo la última disponible. Después organizamos esos vínculos en una fila por decisión y una columna por indicador. La dirección de la decisión es la respuesta que queremos predecir y se mantiene separada de la información previa.

**Puntero y pantalla**

Seguir la relación reunión, vínculo y observación. Señalar el valor 0,1% en la fila final y después y: baja, explicando que cumple otra función.

**Fuentes**

- src/processing/data_unificada.py: vincular y exportar
- notebooks/04_data_unificada.ipynb: caso RPM_20241017
- data/processed/unificada/vinculos_reunion_variable.csv

## Diapositiva 8: Avance actual y próxima evaluación

**4:55-5:40 · Álvaro · 45 segundos**

**Texto hablado**

El avance comprobado incluye las series limpias, el historial de ciento sesenta y una decisiones, la distribución de clases, la trayectoria de la TPM y el mecanismo de integración con un ejemplo histórico de IPC. Lo pendiente es completar los calendarios de publicación de las ocho variables, revisar las versiones históricas de los datos y contrastar el calendario bancario. La muestra final puede ser menor por cobertura. Después construiremos una línea base y una regresión logística, con entrenamiento y prueba en orden cronológico. Todavía no tenemos métricas predictivas. La prioridad es que cada fila represente la información que realmente podía conocerse antes de su decisión.

**Puntero y pantalla**

Recorrer primero los avances y después los pendientes. Terminar en la secuencia entrenamiento anterior y prueba posterior. Mantener visible que no hay resultados de modelos.

**Fuentes**

- notebooks/04_data_unificada.ipynb
- docs/data_unificada.md
- docs/bitacora_avance_entrega_2.md: evaluación prevista
- data/raw/publicaciones_indicadores/cobertura_ejemplo.csv

## Preparación de la grabación

Abrir el PDF de láminas en Xournal++ y mantener este guion fuera de la región capturada. En PowerPoint, las mismas indicaciones quedan en las notas de cada diapositiva. Grabar una prueba breve con micrófono y puntero antes de hacer la toma completa. El PDF de láminas no contiene narración ni animación pregrabada.

Usar el puntero para fechas, valores y relaciones concretas. Evitar moverlo continuamente mientras se habla. Dejar que el rastro desaparezca antes de señalar otra parte de la figura.

Si el ensayo supera seis minutos, resumir primero el detalle de IPC anual en la lámina 2 y los comentarios descriptivos de la trayectoria en la lámina 4. Mantener la pregunta, los conteos, la explicación del corte, los vínculos y la distinción entre avance y resultados de modelos.

## Cifras y límites que deben coincidir

- 2010–2025, con 161 decisiones: 103 mantiene, 31 baja y 27 sube.
- 103/161 = 63,98%, redondeado a 64%. Es descriptivo sobre el registro completo.
- Cobre: Cochilco spot BML/LME, USD/libra y 4.042 cotizaciones.
- Reunión 17/10/2024, corte 16/10. IPC septiembre 0,1%, publicado 08/10. Octubre publicado 08/11.
- Cuatro boletines IPC verificados como ejemplo. Calendario completo de ocho series aún pendiente.
- La trayectoria y la distribución son resultados descriptivos. No hay métricas de modelos.
- El calendario operativo requiere contraste bancario y los datos revisables requieren versiones históricas.

## Edición coordinada

El texto hablado, tiempos, voces y fuentes se mantienen en `src/presentation/contenido_video.json`. Al cambiarlo, regenerar la presentación, sus notas y este guion en la misma revisión. Los scripts y comandos están en `src/presentation/README.md`.
