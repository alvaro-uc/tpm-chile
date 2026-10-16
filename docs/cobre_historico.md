# Cobre: recuperación de 2010–2012 y comparación de fuentes

## Decisión adoptada y serie principal 2010–2025

El **16-10-2026** el equipo decidió usar **Cochilco como fuente única de cobre
para todo 2010–2025**, con precio diario contado/spot BML/LME en USD/libra.
Se evita introducir un cambio de fuente en octubre de 2012. El archivo BCCh se
conserva como referencia para auditoría; no participa en la construcción de
la nueva serie, ni se utiliza para rellenar fechas o ajustar precios.

**Entrada para futuros análisis:**
`data/processed/cobre_cochilco_diario_2010_2025.csv`.

La versión construida tiene **4.042 observaciones**, desde **04-01-2010 hasta
31-12-2025**, en los **192 meses** del intervalo. Se eliminaron **506 repeticiones
idénticas** de los solapamientos. No hay fechas duplicadas ni precios nulos.

| Columna | Significado |
|---|---|
| `fecha` | Fecha informada por Cochilco, `YYYY-MM-DD` |
| `cu_usd_lb` | Precio spot BML/LME en dólares por libra; centavos originales divididos por 100 |
| `fuente` | Cochilco |
| `mercado` | BML/LME spot |
| `unidad` | USD/libra |
| `archivo_origen` | Descarga original de la que procede la observación |

Se usan tres descargas: 2010–2013, 2013–2019 y 2019–2025. Los años 2013 y
2019 se repiten deliberadamente para comprobar la unión. Se exige coincidencia
de precios en las fechas compartidas; solo se elimina la repetición idéntica.
Se conserva la primera descarga como procedencia cuando una fecha aparece dos
veces. Cualquier diferencia entre tramos detiene el procesamiento.

Se comprueban huellas SHA-256, parámetros de metal/bolsa/frecuencia, extremos,
192 meses con observaciones, recuentos por año, fechas únicas y precios positivos.
El informe `docs/cobre_cochilco_validacion.json` contiene los recuentos y extremos
efectivos. El calendario auxiliar
`data/processed/cobre_cochilco_calendario_sin_observacion_2010_2025.csv`
lista días de lunes a viernes sin dato para revisión. **No todos esos días
son faltantes erróneos:** incluyen feriados y cierres de mercado; no se imputan.
Los controles de cobertura son alertas generales, no una certificación de cada
festivo de la Bolsa de Londres.

Reproducir desde las fuentes locales:

```powershell
python -m src.processing.cobre_cochilco
```

Importar en Python:

```python
import pandas as pd
cobre = pd.read_csv("data/processed/cobre_cochilco_diario_2010_2025.csv", parse_dates=["fecha"])
```

No se crean todavía predictores, rezagos ni una tabla final de entrenamiento.
Al integrar con las decisiones TPM se mantendrá el cierre del día hábil previo
y se verificará qué cotización estaba disponible entonces. Esta serie descargada
retrospectivamente no certifica por sí misma horarios ni versiones históricas.

Las secciones siguientes conservan la investigación que motivó esta decisión.

## Qué se encontró

El Excel original `data/raw/cu_usd_lb.xlsx` identifica la serie diaria
`F019.PPB.PRE.100.D`, cobre refinado BML en dólares por libra. Su primera fecha,
05-10-2012, coincide con la primera observación que informa el buscador oficial
del Banco Central. El cuadro BDE permite seleccionar años anteriores porque
incluye otras materias primas, pero la fila de cobre no tiene valores allí.
Por tanto, **no hay evidencia de una omisión del usuario al descargar el archivo**.
La advertencia inicial describía una falta de cobertura para el proyecto,
no un error de descarga confirmado.

Se recuperaron **696 observaciones diarias** de Cochilco, desde 04-01-2010 hasta
04-10-2012, en `data/processed/cu_usd_lb_faltante_2010_2012.csv`.
El 1 de enero y los fines de semana no se inventan como observaciones.
Se conserva el calendario de la fuente, sin interpolar ni rellenar festivos.

## Concepto, unidad y trazabilidad

La consulta oficial de Cochilco es Cobre, diaria, BML/LME. La tabla 2.2 de sus
boletines distingue spot de futuros y las bolsas BML y COMEX; se contrastó el
precio spot BML del 04-01-2010: 338,561 centavos/libra frente a 338,56 en la
exportación. Se conserva la precisión entregada en la descarga: **USD/libra =
centavos/libra ÷ 100**, por lo que el valor procesado es 3,3856.

La descarga ampliada cubre 2010–2013 (1.009 observaciones), para permitir una
comparación con el archivo BCCh. El original y su procedencia se conservan en
`data/raw/cobre_historico/`; la tabla completa de esa descarga está en
`data/processed/cobre_cochilco_diario_2010_2013.csv`.

La columna `fecha` representa la fecha informada por la fuente; no certifica
una hora de disponibilidad ni debe renombrarse como fecha de publicación sin
comprobarla. El boletín mensual es una vía de consulta retrospectiva, no evidencia
de que la cotización diaria solo se conociera al terminar el mes.

## Por qué todavía no se empalman automáticamente

La coincidencia de metal, bolsa y unidad no garantiza observaciones idénticas.
Se compararon **299 fechas comunes** entre 05-10-2012 y 30-12-2013:

| Control | Resultado |
|---|---:|
| Dentro de ±0,005 USD/libra (redondeo a dos decimales de BCCh) | 39 de 299 |
| Diferencia absoluta media | 0,03382469 USD/libra |
| Diferencia absoluta máxima | 0,2102 USD/libra |
| Correlación de niveles | 0,97377 |

Ejemplo: el 08-10-2012 BCCh registra 3,76 y Cochilco 3,6891 USD/libra.
No se atribuye esa diferencia a un rezago o una hora concreta sin evidencia.
Tampoco se desplazan fechas ni se ajustan precios para hacerlos coincidir.
Una correlación alta no demuestra equivalencia metodológica.

`data/processed/cobre_comparacion_2012_2013.csv` permite revisar cada fecha.
`docs/cobre_validacion.json` resume controles regenerables.
El procesador conserva los datos por separado y **no reemplaza el CSV de limpieza
del compañero ni genera una serie BCCh artificialmente extendida**.

La decisión adoptada resuelve la integración usando una única fuente homogénea
para todo 2010–2025: Cochilco. La causa exacta de las discrepancias con BCCh
permanece sin demostrar; no se afirma que una fuente sea incorrecta ni se altera
su calendario para forzar coincidencias.

## Reproducción y validación

```powershell
python -m src.processing.cobre_historico
python -m unittest discover -s tests
```

El notebook `notebooks/03_cobre_historico.ipynb` explica y ejecuta el proceso
localmente. No se cambia el notebook de limpieza existente. El procesamiento
verifica la huella de la descarga, el código de serie del Excel, fechas,
duplicados, valores y amplitud del solapamiento. No instala nuevas dependencias.

Para predecir al cierre del día hábil previo a una decisión de TPM, se mantiene
ese corte: no usar cotizaciones posteriores ni confundir una fecha retrospectiva
con disponibilidad histórica certificada. Antes del modelamiento falta comprobar
horarios/calendarios y posibles revisiones de las fuentes.

## Enlaces oficiales

- [Buscador del Banco Central: serie diaria y primera observación](https://si3.bcentral.cl/Search/Buscar/Index/?st=F019.PPB.PRE.100.D&Idioma=ES).
- [BCCh: precios diarios de productos básicos](https://si3.bcentral.cl/Siete/ES/Siete/Cuadro/CAP_EI/MN_EI11/EI_PROD_BAS_DIARIO/638358101053598187).
- [Cochilco: consulta histórica diaria de metales](https://boletin.cochilco.cl/estadisticas/grafico.asp?tipo_metal=1).
- [Cochilco: precios diarios spot y futuros, enero de 2010](https://boletin.cochilco.cl/productos/boletin.asp?anio=2010&mes=01&tabla=tabla2_2).
