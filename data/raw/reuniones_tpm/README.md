# Fuentes de las reuniones de TPM

Esta carpeta reúne la recopilación local de fechas y evidencias para 2010–2025.
Los archivos se trasladaron sin modificar su contenido. Los JSON son extractos
y transcripciones de documentos oficiales; no son descargas de una API del BCCh.

| Archivo | Contenido |
|---|---|
| `rpm_boletines_2010_2012.json` | 31 comunicados: fecha, frase de decisión, nivel anunciado, URL, página y SHA256 del PDF consultado. |
| `rpm_fuentes_complementarias.json` | Fechas de agosto–diciembre de 2012 y 2013–2014, con referencias oficiales y niveles documentados cuando corresponde. |
| `rpm_archivo_2015_2025.json` | Fechas transcritas del archivo por año, rangos de dos días y corrección de diciembre de 2023. |
| `rpm_memoria_2014.html` | Copia original del Anexo I de la Memoria 2014; contiene doce comunicados. |

La consulta original se realizó el **16 de octubre de 2026**. Las fuentes
conservan sus URLs para volver a comprobarlas. Los boletines PDF completos
fueron una caché temporal y no son necesarios para regenerar la tabla local.

## Proceso reproducible

Abrir `notebooks/02_reuniones_tpm.ipynb`, seleccionar el kernel del entorno
virtual del proyecto y ejecutar todas las celdas desde un kernel limpio.
Funciona con directorio de trabajo en la raíz o en `notebooks/`, no descarga
información y no requiere ejecutar el notebook de limpieza existente.

El notebook explica e inspecciona las fuentes, normaliza las fechas, muestra
la alineación con `data/raw/tpm_bcentral_diaria.xlsx`, valida las etiquetas y
regenera `data/processed/reuniones_tpm_2010_2025.csv`.

Las tablas calculadas se guardan en `data/processed/`; esta carpeta conserva
los insumos de la recopilación. No se copian resultados derivados a `raw`.

El proceso reproduce **la transformación de esta recopilación local**, no
la navegación y transcripción originales ni la extracción de todos los PDF.
Ver `docs/reuniones_tpm.md` para trazabilidad, diccionario y limitaciones.
