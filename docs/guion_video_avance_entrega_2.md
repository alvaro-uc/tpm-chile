# Guion para el video de avance del proyecto de TPM

**Entrega 2 · IMT2200 · Grupo 9 · Base de ensayo al 16-10-2026**

Objetivo de duración: **5:30–5:45**, con límite de seis minutos. El reparto y los tiempos son una propuesta para acordar con el grupo. Cronometrar una lectura real antes de grabar; los cambios de voz y de pantalla también consumen tiempo. Las acotaciones de pantalla no se leen en voz alta.

El texto hablado tiene aproximadamente **590 palabras**. La duración final depende del ritmo y las pausas; reservar margen para presentar las vistas de apoyo.

## Reparto y vistas de apoyo

| Tiempo orientativo | Voz propuesta | Pantalla y función |
|---|---|---|
| 0:00–1:00 | Loreto | Título, pregunta y tres clases objetivo. |
| 1:00–2:10 | Fernando | Inventario de variables y un ejemplo de CSV limpio. |
| 2:10–3:40 | Macarena | Tabla 103/31/27 y ejemplo decisión/corte. |
| 3:40–5:15 | Álvaro | Serie Cochilco, comparación y próximas tareas. |
| 5:15–5:35 | Loreto o cierre compartido | Estado del avance y trabajo siguiente. |

## Texto para ensayar

### Loreto

Nuestro proyecto estudia si podemos anticipar la dirección de las decisiones de Tasa de Política Monetaria del Banco Central de Chile usando información macroeconómica pública. Nos interesa porque la tasa influye en las condiciones de crédito, ahorro e inversión.

La pregunta es cuánto permiten anticipar esos indicadores si la próxima decisión será subir, mantener o bajar la tasa. Trabajamos con el período cerrado de 2010 a 2025. El resultado que buscamos clasificar es la dirección de cada decisión, no el valor exacto de la tasa.

Desde la propuesta nos hemos concentrado en recopilar y preparar los datos y en definir qué información podía conocerse antes de cada decisión. Ese punto fue una de las principales observaciones del profesor.

### Fernando

Recopilamos series oficiales de TPM, inflación, IMACEC, desempleo, dólar, cobre y expectativas de TPM. Algunas son diarias y otras mensuales, por lo que sus fechas no se pueden combinar directamente.

Conservamos los archivos originales y generamos CSV separados mediante notebooks y funciones en Python. La limpieza identifica los encabezados reales, convierte la primera columna a fecha, conserva la segunda como valor numérico y ordena las observaciones. Revisamos que los ocho CSV actuales mantengan los valores de los Excel de origen.

También distinguimos qué representa cada variable. El IMACEC descargado es un índice y el archivo de IPC anual tiene frecuencia anual; no debe confundirse con una serie mensual de inflación interanual. Antes de integrarlas falta comprobar sus fechas de publicación y posibles revisiones.

<!-- pagina -->

### Macarena

La unidad de análisis es una decisión de política monetaria. Por eso recopilamos fechas de reuniones: observar solo los cambios diarios de la tasa habría dejado fuera las decisiones que la mantuvieron.

El historial reúne 161 decisiones: 103 mantenciones, 31 bajas y 27 subidas. Esto muestra que las clases están desbalanceadas. Más adelante tendremos que comparar los modelos con una línea base y mirar su comportamiento por clase, además del acierto total.

Definimos predecir al cierre del día hábil anterior al anuncio. Por ejemplo, para la decisión del 15 de junio de 2010, el corte es el 14 de junio. Los indicadores utilizados deben haber estado publicados hasta ese corte. La tasa posterior sirve para construir la respuesta, pero no puede entrar como predictor.

El calendario actual se apoya en las fechas de la serie diaria de TPM. Aún falta contrastarlo con un calendario bancario independiente y resolver la disponibilidad histórica de cada indicador.

### Álvaro

Una decisión concreta fue cambiar la fuente de cobre para todo el período. La serie diaria descargada del Banco Central comienza en octubre de 2012. Recuperamos información de Cochilco y comparamos ambas fuentes en fechas comunes.

Encontramos diferencias superiores al redondeo: en 299 fechas comparadas, solo 39 coincidían dentro de medio centavo de dólar por libra. No asumimos que alguna fuente fuera incorrecta ni aumentamos la tolerancia para unirlas.

Elegimos usar exclusivamente el precio diario spot de la Bolsa de Metales de Londres publicado por Cochilco. La serie tiene 4.042 cotizaciones desde enero de 2010 hasta diciembre de 2025. Conservamos las descargas, convertimos centavos a dólares por libra y verificamos que los tramos se unieran con precios coincidentes. No inventamos observaciones para los días sin dato.

El siguiente paso es integrar las variables según su publicación, definir transformaciones y construir el análisis exploratorio sobre esa base. Después evaluaremos líneas base y modelos simples respetando el orden temporal.

### Cierre

Nuestro avance actual es una preparación documentada y reproducible de los datos y del experimento. Todavía no tenemos resultados de modelos. La prioridad es que la futura evaluación represente información que realmente podía conocerse antes de cada decisión.

## Cifras que deben mantenerse iguales en todas las tomas

- Período del estudio: 2010–2025.
- Historial: 161 decisiones; 103 mantiene, 31 baja, 27 sube.
- Cobre elegido: Cochilco, spot BML/LME, USD/libra; 4.042 cotizaciones.
- Comparación histórica de fuentes: 299 fechas; 39 dentro de ±0,005 USD/libra.
- Corte acordado: cierre del día hábil anterior al anuncio.
- Estado: preparación y validación; integración temporal y modelos pendientes.

En el ensayo, si el video supera el límite, resumir el ejemplo de IPC anual y los detalles de la tolerancia antes de acelerar la lectura. Conservar siempre la problemática, la pregunta, los datos y los resultados reales del avance.
