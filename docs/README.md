# Fuentes y decisiones de datos

## Serie de TPM

El archivo fuente versionado es `data/raw/tpm_bcentral_diaria.xlsx`. Se obtuvo de la Base de Datos Estadísticos del Banco Central de Chile y contiene las hojas `Cuadro`, `Metadatos` y `Series`. La hoja `Series` identifica el código `F022.TPM.TIN.D001.NO.Z.D`, con descripción “Tasa de política monetaria (TPM) (porcentaje)”. La unidad es porcentaje y la frecuencia indicada por el Banco Central es diaria.

En `Cuadro`, los encabezados están en la fila 3: la columna A contiene `Periodo` y la B contiene la TPM en porcentaje; los registros comienzan en la fila 4. La copia revisada contiene 7.391 observaciones desde el 7 de febrero de 1997 hasta el 22 de septiembre de 2026. La tasa se repite en días hábiles mientras no cambie la decisión. En la serie hay 123 cambios efectivos posteriores al valor inicial; las filas diarias repetidas no son reuniones ni decisiones nuevas. Hay saltos de calendario por fines de semana y feriados.

La pregunta del estudio se refiere a anticipar decisiones de TPM. Para el análisis predictivo, definiremos observaciones alrededor de las fechas de decisión y construiremos cada predictor solo con información que ya estaba disponible antes de la reunión. No trataremos cada fila diaria repetida como una decisión independiente. El período principal propuesto sigue siendo 2010–2025; el archivo fuente completo se conserva sin recortarlo y el filtro se aplicará en el procesamiento.

### Revisión de metadatos de la descarga

La hoja `Series` identifica la TPM, pero la nota de metodología de la hoja `Metadatos` describe la Tasa de Interés Interbancaria (TIB), que es otra medida. No utilizaremos esa nota como definición metodológica de la TPM. La definición oficial del Banco Central describe la TPM como la tasa objetivo para las operaciones interbancarias que procura alcanzar mediante sus instrumentos de política monetaria.

También hay una diferencia de fecha dentro de la copia: `Metadatos` indica actualización al 21 de septiembre de 2026, mientras `Cuadro` incluye una observación del 22 de septiembre. La ficha web consultada del Banco Central indicaba como última observación el 21 de septiembre. Mantendremos intacta la descarga original y confirmaremos esa observación con una descarga posterior antes de usarla como corte analítico.

Fuentes oficiales consultadas:

- [Ficha diaria de la TPM](https://si3.bcentral.cl/Bdemovil/BDE/Series/MOV_SC_TI1)
- [Serie BDE F022.TPM.TIN.D001.NO.Z.D](https://si3.bcentral.cl/siete/ES/Siete/Cuadro/CAP_EST_OMA/MN_EST_OMA/EM_OMA_30?idSerie=F022.TPM.TIN.D001.NO.Z.D)
- [Calendario oficial de reuniones de política monetaria 2026](https://www.bcentral.cl/documents/33528/6833519/Calendario%2BRPM%2C%2BRPF%2C%2BIPoM%2C%2BIEF%2B2026.pdf/a64d59c3-bb40-cf21-c3c0-583f61304a6c?t=1759839840190)

## Reglas para las fuentes nuevas

Para cada serie, registrar definición, unidad, frecuencia original, fuente oficial, identificador o URL de referencia, fecha de consulta, período disponible y transformaciones. Registrar fechas de publicación/disponibilidad para evitar filtración temporal.

El equipo trabajará con archivos locales versionados, sin APIs ni scripts de descarga automática. Mantener intactos los originales en `data/raw/`; guardar las tablas regenerables en `data/processed/`. Antes de versionar un archivo, comprobar que sea público, liviano y que no incluya información restringida.

Mantener aquí el diccionario de datos, la regla para etiquetar las decisiones como sube/mantiene/baja, la alineación de frecuencias, el tratamiento de valores faltantes y las fechas de corte.
