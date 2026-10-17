# Notebooks

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

