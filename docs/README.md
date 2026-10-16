# Fuentes y decisiones de datos

## Inventario de archivos originales

Los Excel conservan sus hojas `Cuadro`, `Metadatos` y `Series`. Los datos no se reescriben dentro de esos archivos. El código de serie indicado abajo sirve para identificar la serie del Banco Central en su exportación; el equipo trabajará leyendo los archivos locales y no mediante APIs ni descargas automáticas.

| Archivo | Variable y definición | Unidad / frecuencia | Cobertura en el archivo | Fuente y código de serie |
|---|---|---|---|---|
| `data/raw/tpm_bcentral_diaria.xlsx` | Tasa de Política Monetaria | Porcentaje / diaria | 1997-02-07 a 2026-09-22 | Banco Central de Chile · `F022.TPM.TIN.D001.NO.Z.D` |
| `data/raw/clp_usd.xlsx` | Dólar observado, tipo de cambio nominal | Pesos por dólar / diaria | 1982-08-09 a 2026-09-23 | Banco Central de Chile · `F073.TCO.PRE.Z.D` |
| `data/raw/cu_usd_lb.xlsx` | Precio del cobre refinado BML | Dólares por libra / diaria | 2012-10-05 a 2026-09-23 | Bolsas de metales · `F019.PPB.PRE.100.D` |
| `data/raw/desempleo_total_mensual.xlsx` | Tasa de desocupación total, no ajustada | Porcentaje / mensual | 2010-03 a 2026-07 | INE, según descripción de la serie · `F049.DES.TAS.INE9.10.M` |
| `data/raw/ipc_general_mensual.xlsx` | IPC general, variación mensual | Porcentaje / mensual | 1928-03 a 2026-08 | INE · `F074.IPC.VAR.Z.Z.C.M` |
| `data/raw/ipc_general_anual.xlsx` | IPC general, variación anual histórica de diciembre | Porcentaje / anual | 1929 a 2025 | INE · `F074.IPC.VAR.Z.Z.C.A` |
| `data/raw/imacec_empalmado_original.xlsx` | IMACEC empalmado, serie original, referencia 2018=100 | Índice / mensual | 1996-01 a 2026-07 | Banco Central de Chile · `F032.IMC.IND.Z.Z.EP18.Z.Z.0.M` |
| `data/raw/exp_tpm_mensual_mediana.xlsx` | Mediana mensual de expectativas de TPM | Porcentaje / mensual | 2001-09 a 2026-09 | Banco Central de Chile · `F089.TPM.TAS.11.M` |

La cobertura muestra todo el período guardado en cada Excel. El análisis principal propuesto se limita a 2010–2025. Se filtrará ese período en el procesamiento, sin recortar los archivos originales. IPC mensual y anual son medidas relacionadas, pero no intercambiables; no duplicar ambas como predictores sin una justificación analítica.

## Lectura e interpretación

El historial de reuniones y la regla de corte acordada están en
[`reuniones_tpm.md`](reuniones_tpm.md). La tabla por decisión se conserva aparte
en `data/processed/reuniones_tpm_2010_2025.csv`, sin modificar los Excel originales.
Las tres fuentes JSON `data/raw/reuniones_tpm/rpm_*.json` y el anexo HTML de la Memoria 2014
documentan la recopilación puntual autorizada; regenerar la tabla no usa red.
El notebook `notebooks/02_reuniones_tpm.ipynb` inspecciona esos insumos y
explica la construcción y validación de la tabla por decisión.

- En la hoja `Cuadro`, los encabezados están en la fila 3: columna A `Periodo`, columna B el valor. Los registros comienzan en la fila 4.
- Las series diarias contienen días de actividad/publicación, no una fila por reunión. La TPM se mantiene constante entre cambios de decisión. El dólar y el cobre también tienen calendarios de publicación propios.
- La serie EEE tiene en sus metadatos “10 a 13 días del mes informado”. No interpretarlo automáticamente como publicación en el mes siguiente: verificar la fecha efectiva de cada encuesta. La referencia a fines de mes describe el horizonte de la expectativa de TPM, no que las respuestas se recojan al cierre del mes.
- El IMACEC tiene desfase de publicación de 31 días terminado el mes y sus cifras se identifican como preliminares en los metadatos.
- Para el dólar observado, revisar la nota metodológica del libro: describe operaciones del día hábil bancario previo a la publicación. Aunque el campo de metadatos dice “Sin rezago”, no asumir disponibilidad contemporánea antes de verificar las fechas de publicación.
- Las series de IPC tienen cambios de base y empalmes históricos descritos en sus metadatos. Mantener el mismo concepto y transformación durante todo el período analítico.
- La nota de metodología del libro de TPM menciona TIB, aunque la hoja `Series` identifica la TPM. No usar esa nota de TIB como definición de la variable TPM.
- En la copia de TPM, los metadatos indican actualización al 21 de septiembre de 2026 y `Cuadro` llega al 22. En dólar y cobre, los metadatos indican actualización al 22, mientras los datos llegan al 23. Confirmar estas últimas observaciones en una versión posterior antes de usarlas como corte analítico.
- El Excel anual de IPC presenta observaciones con fechas de enero, aunque su descripción indica el dato anual histórico de diciembre. Interpretar el período según esa descripción, no como una inflación de enero.

## Retroalimentación del profesor

`docs/retroalimentacion_profesor.pdf` conserva el documento descargado con comentarios del profesor. Se mantiene como referencia para el equipo; las decisiones de implementación se acordarán entre los integrantes.

## Reglas para nuevas fuentes

Para cada serie nueva, registrar nombre de archivo, variable, unidad, frecuencia, cobertura, fuente, identificador de serie y rezago/fecha de publicación. Mantener intactos los originales en `data/raw/` y guardar tablas regenerables en `data/processed/`. Antes de añadir un archivo al repositorio, comprobar que sea público, pequeño y que no incluya información restringida.
