# Notebooks

El [estudio final](05_estudio_final_tpm.ipynb) integra 161 anuncios, explora seis
predictores por clase y evalúa 100 reuniones ordinarias posteriores al bloque
inicial. Regenera las tablas y gráficos en
 [output/entrega_final/resultados](../output/entrega_final/resultados/). Usa los
archivos fuente y CSV de preparación versionados. Instala las dependencias de
la raíz y ejecuta todas las celdas en el entorno del proyecto.

## Reproducir la entrega desde los insumos originales

En una copia del paquete, conserva las carpetas `data/raw/`, `docs/`,
`notebooks/` y `src/`. Incluye también `requirements.txt`, el README y, si se
ejecutarán las comprobaciones, `tests/`. Prepara un entorno con
`python -m pip install -r requirements.txt`. El entorno de referencia es Python
3.14.3. Ejecuta desde la raíz con ese mismo intérprete.

1. Ejecuta [01_limpieza_y_procesamiento.ipynb](01_limpieza_y_procesamiento.ipynb)
   con un kernel limpio para generar los CSV de series en `data/processed/`.
2. Regenera la serie de cobre y los anuncios oficiales.

   ```powershell
   rtk proxy ./.venv/Scripts/python.exe -m src.processing.cobre_cochilco
   rtk proxy ./.venv/Scripts/python.exe -m src.processing.reuniones_tpm
   ```

3. Ejecuta todas las celdas de [05_estudio_final_tpm.ipynb](05_estudio_final_tpm.ipynb)
   en un kernel limpio. Desde allí se reconstruye la integración que usa el
   estudio, y se exportan métricas, predicciones y gráficos. Compara
   `output/entrega_final/resultados/metricas.csv` con la versión entregada y
   coteja las cifras de las láminas.

Este flujo se comprobó en una copia aislada sin `data/processed/` ni
`output/` al inicio. Los ocho CSV finales regenerados coincidieron con las
salidas de referencia. Si `rtk` no está instalado, ejecuta directamente el
comando que sigue a `rtk proxy`.

Si usas Codex para ejecutar notebooks por terminal, instala también `nbclient`
en el mismo entorno. Para la ejecución interactiva basta el kernel declarado
por el proyecto. Las salidas versionadas permiten revisar el análisis antes de
regenerarlo. Conserva la carpeta `docs/` porque allí se escribe la validación
de Cochilco durante el paso 2.

`04_data_unificada.ipynb` importa y explora las ocho series, explica la relación
entre reuniones y observaciones, prepara la captura de publicaciones y exporta
vínculos auditables y una tabla ancha. Incluye cuatro láminas y un caso IPC real
documentado (reunión 17/10/2024). Recorta copias a 2010–2025 y separa una reserva
de 2009. Los otros períodos sin evidencia quedan pendientes; ver
`docs/data_unificada.md`.

Usa esta carpeta para notebooks numerados y reproducibles. El notebook final debe poder ejecutarse de principio a fin partiendo de los datos documentados en `data/raw/`.

`02_reuniones_tpm.ipynb` documenta y procesa la recopilación de reuniones de
TPM de 2010–2025. Inspecciona las fuentes de `data/raw/reuniones_tpm/`, alinea
las decisiones con el Excel original de TPM diaria, valida fechas y niveles
y regenera `data/processed/reuniones_tpm_2010_2025.csv`.

Seleccionar el kernel del entorno virtual del proyecto y ejecutar todas las
celdas desde un kernel limpio. El notebook encuentra la raíz desde la carpeta
del proyecto o `notebooks/` y utiliza las dependencias existentes; no descarga
datos ni depende de ejecutar `01_limpieza_y_procesamiento.ipynb`.

