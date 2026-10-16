# Notebooks

Usa esta carpeta para notebooks numerados y reproducibles. El notebook final debe poder ejecutarse de principio a fin partiendo de los datos documentados en `data/raw/`.

`02_reuniones_tpm.ipynb` documenta y procesa la recopilación de reuniones de
TPM de 2010–2025. Inspecciona las fuentes de `data/raw/reuniones_tpm/`, alinea
las decisiones con el Excel original de TPM diaria, valida fechas y niveles
y regenera `data/processed/reuniones_tpm_2010_2025.csv`.

Seleccionar el kernel del entorno virtual del proyecto y ejecutar todas las
celdas desde un kernel limpio. El notebook encuentra la raíz desde la carpeta
del proyecto o `notebooks/` y utiliza las dependencias existentes; no descarga
datos ni depende de ejecutar `01_limpieza_y_procesamiento.ipynb`.

