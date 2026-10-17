# Estado del proyecto al 17 de octubre de 2026

## Avances incorporados

- Se conserva el análisis de decisiones TPM incorporado por el equipo en
  `notebooks/04_analisis_decisiones_tpm.ipynb`, junto con su actualización de
  dependencias.
- `notebooks/04_data_unificada.ipynb` integra ocho series mediante IDs estables
  de reunión y observación, para 161 decisiones de 2010–2025. Conserva 2009
  como antecedente separado y exporta vínculos auditables y una tabla ancha.
- La selección distingue fecha de referencia, fecha de publicación y versión
  histórica. El ejemplo IPC incluye cuatro publicaciones de 2024 y evita usar
  información posterior al corte de cada decisión. La captura editable y sus
  fuentes están versionadas; las salidas derivadas se regeneran localmente.
- Se agregan pruebas de integración y figuras explicativas reproducibles.
- Se incorpora una presentación de ocho láminas con gráficos editables,
  notas, PDF y guion sincronizado. La pauta dura 5:40; no es una medición
  del video. Los archivos de la revisión v4 están en `output/` y el procedimiento
  de regeneración en `src/presentation/README.md`.
- Ya se compartió con el equipo por WhatsApp un video de ensayo de la
  exposición, según lo informado por Álvaro. El video no forma parte del repo.

## Estado de los resultados

El registro contiene 103 mantenciones, 31 bajas y 27 subidas. Son resultados
descriptivos; todavía no se reportan métricas predictivas. La tabla unificada
no constituye una base histórica completamente documentada y lista para
entrenar: el ejemplo de IPC cubre solo un intervalo de 2024.

## Próximos pasos

1. Completar y revisar fechas de publicación, cobertura y versiones históricas
   para las ocho series y el resto del período.
2. Contrastar los cortes operativos con un calendario bancario independiente
   y acordar los predictores, revisando la pertinencia del IPC anual y la
   redundancia entre TPM diaria y TPM previa.
3. Construir una regla base y los clasificadores con separación cronológica
   de entrenamiento y prueba, una vez revisada la disponibilidad de datos.
4. Recoger comentarios del ensayo, ajustar reparto y tiempos y preparar la
   grabación final.

## Verificación

Las 18 pruebas de `python -m unittest discover -s tests -v` pasan en el entorno
local. También se ejecutaron, en orden y en un proceso Python limpio, las 17
celdas de código del notebook de integración. Se obtienen 161 reuniones y cero
filas con las ocho variables y calendarios documentados, coherente con la
cobertura parcial. Esta verificación no ejecuta la interfaz ni el kernel Jupyter.
Los scripts de presentación requieren el runtime de documentos indicado
en su README; no se incluye ese runtime en el repositorio.
