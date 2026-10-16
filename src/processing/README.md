# Procesamiento

Añadir funciones para validar fechas y unidades, tratar faltantes, alinear frecuencias, integrar indicadores, construir rezagos y crear la etiqueta de decisión de TPM. Guardar salidas regenerables en `data/processed/`.

La serie de TPM tiene frecuencia diaria, pero su valor se mantiene igual entre decisiones. El análisis de anticipación debe definirse por fechas de reunión y usar solo información disponible antes de cada decisión. El alcance inicial del estudio es 2010–2025, aunque el archivo fuente conserva todo el período disponible.

`python -m src.processing.reuniones_tpm` genera la tabla por decisión desde
fuentes locales y el Excel diario original, sin depender de los CSV limpios.
Incluye fecha de decisión, corte al cierre del día hábil anterior, niveles de
TPM antes y después y etiqueta `sube/mantiene/baja`. Ver `docs/reuniones_tpm.md`
para fuentes, trazabilidad y límites del calendario operativo.
