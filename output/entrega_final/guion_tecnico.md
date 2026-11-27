# Guion técnico de grabación y edición

Pauta de 7:55 y 1028 palabras habladas. Los tiempos son puntos de partida para el ensayo y se reajustan sobre la toma elegida. El reparto entre integrantes es propuesto. Una voz puede grabar toda la presentación.

Abre [las láminas para OBS](laminas_para_grabar.pdf) y [el guion de lectura](guion_de_lectura.pdf) en ventanas separadas. La [pauta de grabación](pauta_grabacion.pdf) describe la prueba de captura.

## 1. ¿Podemos anticipar al Banco Central?

**0:00–0:21 · 21 s · Voz propuesta: Álvaro.**

Marca Baja, Mantiene y Sube a medida que se nombran.

**Texto hablado.** Cuando el Banco Central cambia su tasa de política monetaria, o TPM, influye en el costo del crédito. Nos preguntamos si, el día hábil anterior a cada anuncio, podíamos anticipar una de tres respuestas: baja, se mantiene o sube.

**Referencia para cotejar.** Registro de decisiones del BCCh, 2010–2025

## 2. Una fila por anuncio

**0:21–0:46 · 25 s · Voz propuesta: Álvaro.**

Señala las 103 mantenciones y luego compara la franja azul entre períodos.

**Texto hablado.** Una tasa diaria que queda igual puede significar que ese día hubo una reunión y el Banco Central decidió mantenerla. Por eso reconstruimos el calendario oficial y armamos una fila por anuncio. De los 161 anuncios, 103 fueron mantenciones. El gráfico muestra cómo cambió el reparto con los años.

**Referencia para cotejar.** notebooks/02_reuniones_tpm.ipynb · output/entrega_final/resultados/decisiones_por_periodo.csv

## 3. La fecha del dato y la de publicación

**0:46–1:23 · 37 s · Voz propuesta: Loreto.**

Marca el corte del 16/10. Contrasta las publicaciones del 08/10 y del 08/11.

**Texto hablado.** Para cada pronóstico usamos lo que ya se sabía al cierre del día hábil anterior. A ese momento le llamamos corte. Para la reunión del 17 de octubre de 2024, el corte fue el día 16. El IPC mide cómo cambian los precios. El de septiembre ya se conocía desde el 8 de octubre. El de octubre describe los precios de ese mes y se publicó el 8 de noviembre. Al cierre del 16 solo se conocía el de septiembre.

**Referencia para cotejar.** INE, boletines del IPC de septiembre y octubre de 2024 · data/raw/publicaciones_indicadores/ipc_ejemplo_2024.csv

## 4. Por qué solo añadimos el dólar

**1:23–2:21 · 58 s · Voz propuesta: Loreto.**

Marca fecha y versión. Recorre las dificultades y termina en «161 de 161».

**Texto hablado.** Queríamos sumar inflación, actividad, empleo, cobre y expectativas. Para cada reunión teníamos que comprobar dos cosas: cuándo salió el dato y qué valor se publicó. Si usamos una cifra corregida meses después, le damos al modelo información del futuro. En el IPC comprobamos la fecha y el valor en dos reuniones. Para actividad y desempleo faltaron las cifras de la época.

Recuperamos las cotizaciones del cobre con Cochilco. Quedó pendiente verificar su hora de publicación y, en la encuesta, contrastar las fechas. Para el dólar observado, el Banco Central documenta cuándo rige cada cotización. Así respaldamos los datos al corte en los 161 anuncios. Por eso fue el único indicador que añadimos al historial de la TPM en la prueba principal.

**Referencia para cotejar.** output/entrega_final/resultados/cobertura.csv · docs/data_unificada.md · docs/cobre_historico.md · BCCh, ficha metodológica del dólar observado F073.TCO.PRE.Z.D

## 5. Así se ve la tabla de entrenamiento

**2:21–3:05 · 44 s · Voz propuesta: Fernando.**

Sigue la fila del 15/06. Marca 50 en julio y la respuesta en azul.

**Texto hablado.** Estas son tres filas reales. En junio, la tasa vigente era 0,50 por ciento. El último cambio y la suma de los tres anteriores eran cero. En julio ya vemos un cambio previo de cincuenta puntos base, o medio punto porcentual. También medimos cuánto cambió el precio de un dólar en pesos desde veinte cotizaciones atrás.

La columna azul dice cómo decidió el Banco Central. Para entrenar usamos esa respuesta en reuniones pasadas. Para pronosticar la siguiente, ingresamos los datos conocidos al corte.

**Referencia para cotejar.** output/entrega_final/resultados/panel_por_reunion.csv · src/processing/estudio_final.py, ESTADO, DOLAR y evaluar

## 6. Dólar y actividad antes de cada decisión

**3:05–3:57 · 52 s · Voz propuesta: Fernando.**

Señala el cero, el punto verde y su línea. Luego compara 2,42 y 7,04 en IMACEC.

**Texto hablado.** En el gráfico del dólar, cero significa que su precio en pesos quedó igual. Si ordenamos los cambios del dólar antes de las nueve bajas de TPM, el punto verde es el valor de en medio, más 1,85 por ciento. La línea abarca la mitad central de los valores y cruza el cero. El dólar subió en cinco de esas nueve reuniones. Antes de las alzas de TPM, la mediana quedó bajo cero.

El IMACEC mide la actividad económica de Chile cada mes. Aquí la comparamos con el mismo mes del año anterior. El crecimiento mediano fue 7,04 por ciento en las alzas y 2,42 en las bajas. Las cifras descargadas pueden incluir revisiones posteriores a la reunión.

**Apoyo para el expositor.**

- La línea verde del dólar va de −0,37 % a +3,14 %. Queda fuera aproximadamente un cuarto de los valores por abajo y otro cuarto por arriba. El punto es la mediana. Antes de las alzas de TPM, el dólar cayó en 7 de 12 casos.
- El patrón del IMACEC describe este grupo de reuniones. Para probarlo como predictor habría que reconstruir las cifras que estaban publicadas en cada fecha de corte.

**Referencia para cotejar.** output/entrega_final/resultados/eda_por_clase.csv · notebooks/05_estudio_final_tpm.ipynb · output/entrega_final/resultados/panel_por_reunion.csv, primeras 60 reuniones ordinarias

## 7. Cómo comparamos los pronósticos

**3:57–4:53 · 56 s · Voz propuesta: Fernando.**

Sigue enero con 60 y febrero con 61. Luego señala los cuatro métodos.

**Texto hablado.** Partimos con sesenta reuniones que ya habían ocurrido. Con ellas entrenamos el modelo para pronosticar la reunión de enero de 2015. Una vez anunciada la decisión de enero, la incorporamos y entrenamos con sesenta y una reuniones para pronosticar febrero. Repetimos ese proceso hasta tener cien pronósticos. En cada paso, el modelo solo podía aprender de reuniones anteriores.

En esas mismas cien reuniones comparamos cuatro métodos. La mayoría histórica elige la decisión más frecuente hasta entonces. Persistencia repite la última: si la TPM bajó, pronostica otra baja. La regresión logística aprende de las reuniones anteriores y asigna una probabilidad a baja, mantención y alza. Su pronóstico es la opción con mayor probabilidad. Una versión recibe el historial de la TPM. La otra añade el dólar.

**Referencia para cotejar.** notebooks/05_estudio_final_tpm.ipynb, protocolo y predicciones · src/processing/estudio_final.py, evaluar

## 8. Cómo leer el F1 macro

**4:53–5:57 · 64 s · Voz propuesta: Macarena.**

Marca los 64 aciertos de mayoría y compara las tres barras cercanas a 0,69.

**Texto hablado.** El F1 macro es un puntaje de cero a uno que resume qué tan bien reconocemos los tres tipos de decisión. Les da el mismo peso. ¿Por qué nos importa? En esta prueba, decir siempre ‘mantiene’ acierta 64 de cien y deja escapar todas las bajas y alzas.

Veamos las bajas con la logística que usa dólar. Hubo 21 bajas reales y detectó diez. Al mismo tiempo, pronosticó quince bajas y acertó diez. Así medimos dos cosas: cuántas bajas detectó y cuántas veces acertó cuando avisó de una baja. El F1 combina esas dos proporciones en 0,56.

Repetimos el cálculo para mantenciones y alzas. Al promediar los tres puntajes, con un tercio de peso cada uno, obtenemos el F1 macro. El uno sería un resultado perfecto en las tres clases. Persistencia y las dos logísticas quedan cerca de 0,69 en esa escala.

**Apoyo para el expositor.**

- El F1 macro es el promedio simple de los F1 de baja, mantención y alza. Va de 0 a 1. Cada clase aporta un tercio.
- Para bajas, sensibilidad = 10/21 y precisión = 10/15. El F1 es la media armónica: 2 × precisión × sensibilidad ÷ (precisión + sensibilidad). Equivale a 2 × 10 ÷ (21 + 15) = 0,556.
- Con dólar, (0,556 + 0,826 + 0,692) ÷ 3 ≈ 0,691. Su exactitud fue 76 de 100. Con mayoría, (0 + 0,780 + 0) ÷ 3 ≈ 0,260.

**Referencia para cotejar.** output/entrega_final/resultados/metricas.csv · output/entrega_final/resultados/predicciones.csv

## 9. Dónde se perdieron aciertos

**5:57–6:30 · 33 s · Voz propuesta: Macarena.**

Sigue la fila Baja a la derecha. Compara después los aciertos de ambos métodos.

**Texto hablado.** Miremos la primera fila de la tabla derecha. Son las 21 bajas reales. Diez aparecen en la columna ‘Baja’, porque la logística con dólar las acertó. Las otras once aparecen en ‘Mantiene’, que fue el pronóstico equivocado. Las celdas sombreadas muestran los aciertos.

Si comparamos ambas tablas, persistencia detectó más bajas y más alzas. La logística con dólar acertó más mantenciones, 57 frente a 51. Así vemos dónde quedaron las diferencias entre puntajes parecidos.

**Referencia para cotejar.** output/entrega_final/resultados/predicciones.csv, 100 reuniones ordinarias

## 10. ¿Qué pasa si usamos la encuesta?

**6:30–7:21 · 51 s · Voz propuesta: Macarena.**

Sigue el ejemplo de la regla. Compara 0,712 y 0,847 y marca el supuesto del día 13.

**Texto hablado.** En el avance, la encuesta del Banco Central parecía ayudar a pronosticar. Quisimos saber cuánto dependía de cuándo la dábamos por disponible. Probamos una regla aparte: si la tasa esperada a fin de mes era menor que la vigente, pronosticábamos baja. Si era igual o mayor, mantención o alza.

Con la encuesta del mes anterior, esa regla obtuvo 0,712 de F1 macro en las mismas cien reuniones. Si usábamos la del mes actual cuando el corte caía el día trece o después, daba 0,847. Esa fecha era un supuesto. Si la publicación real llegó después del corte, el pronóstico habría usado información futura. Por eso dejamos la encuesta fuera del modelo principal.

**Apoyo para el expositor.**

- La EEE resume la mediana de las expectativas para fin de mes. La usamos en una regla independiente de la regresión logística. La ficha de la serie indica 10 a 13 días del mes informado. De ahí viene el supuesto del día 13.
- Mantuvimos la regla y las 100 reuniones fijas. La regla del día 13 usa la encuesta del mes previo antes de ese día y cambia 13 pronósticos. El puntaje pasa de 0,712 a 0,847. Falta cotejar la fecha efectiva de cada encuesta para saber si ese puntaje se sostiene con datos disponibles al corte.

**Referencia para cotejar.** BDE Banco Central de Chile, serie EEE F089.TPM.TAS.11.M · output/entrega_final/resultados/sensibilidad_eee.csv

## 11. Qué pudimos anticipar

**7:21–7:55 · 34 s · Voz propuesta: Macarena.**

Compara los tres puntajes. Termina en el hallazgo sobre los datos al corte.

**Texto hablado.** Volvamos a la pregunta inicial. ¿Qué pudimos anticipar antes de cada anuncio? En cien reuniones, repetir la última decisión fue una referencia difícil de superar. La logística usando el historial de la TPM quedó muy cerca. Al añadir el dólar, su F1 macro bajó levemente.

Para evaluar los demás indicadores con el mismo criterio, necesitamos recuperar las publicaciones originales y sus fechas. El aporte de este proyecto es un registro por reunión y una prueba que respeta lo que se sabía antes de cada anuncio.

**Referencia para cotejar.** notebooks/05_estudio_final_tpm.ipynb, conclusiones y limitaciones
