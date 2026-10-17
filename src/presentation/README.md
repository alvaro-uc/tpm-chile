# Presentación y guion del video de avance

Ocho láminas 16:9 para un ensayo de 5:40, con margen hasta seis minutos.
El contenido responde a la consigna descrita por el usuario, sin acceso
independiente a Canvas. Las notas y el guion distinguen resultados descriptivos,
el ejemplo de integración ya documentado y las publicaciones pendientes.

## Archivos

- [Presentación editable v4](../../output/presentacion/avance_tpm_6_min_v4.pptx).
- [Láminas PDF v4](../../output/pdf/avance_tpm_6_min_v4.pdf).
- [Guion del presentador PDF v4](../../output/pdf/guion_presentador_tpm_v4.pdf).
- [Guion en Markdown](../../docs/guion_video_avance_entrega_2.md).

- `contenido_video.json`: fuente única de títulos, voces propuestas, texto hablado,
  tiempos, indicaciones del puntero y fuentes. El reparto puede cambiarse.
- `preparar_datos.py`: extrae conteos, trayectoria diaria y marcadores desde datos
  locales. El gráfico usa escalones reales, sin interpolar la TPM.
- `crear_presentacion.mjs`: crea tablas, gráficos y diagramas editables, incluye
  notas y valida el PPTX con Artifact Tool. Los workbooks incrustados conservan
  los valores de los gráficos como una instantánea derivada de los CSV locales.
- `renderizar_final.mjs`: reabre el PPTX final y genera vistas previas.
- `exportar_pdf_y_guion.py`: genera el PDF de láminas, el PDF con guion al lado
  de cada imagen y actualiza `docs/guion_video_avance_entrega_2.md`.

Las láminas PDF son imágenes de 1920×1080 para presentar y anotar. No contienen
la voz ni los gestos del puntero. El PowerPoint conserva los gráficos y tablas
editables. Se validó con Artifact Tool, sin afirmar una prueba en Microsoft
PowerPoint ni una grabación en Xournal++.

## Regeneración local

Requiere los CSV limpios y el runtime de documentos de Codex disponible en esta
máquina. Los scripts usan las rutas devueltas por `load_workspace_dependencies`.
Para otra máquina, actualizar esas rutas. No requieren red para obtener datos.

Desde la raíz, elegir una revisión nueva, por ejemplo `v5`, porque la validación
no sobrescribe un PPTX final existente:

```powershell
rtk proxy .venv/Scripts/python.exe -m src.presentation.preparar_datos
rtk proxy 'C:/Users/56974/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' src/presentation/crear_presentacion.mjs v5
rtk proxy 'C:/Users/56974/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' src/presentation/renderizar_final.mjs v5
rtk proxy 'C:/Users/56974/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' src/presentation/exportar_pdf_y_guion.py v5
```

El PPTX queda en `output/presentacion/` y ambos PDF en `output/pdf/`.
Los datos intermedios, las vistas de revisión y el informe técnico quedan
en `.build/presentacion/`, ignorado por Git. Al modificar el guion, regenerar
los tres formatos en la misma revisión para conservar su correspondencia.

## Ensayo

Abrir el PDF de láminas en Xournal++. Mantener el guion fuera de la región
capturada o en otro dispositivo. Cronometrar una toma real con las transiciones
y los gestos. Los tiempos son una pauta, no una duración de video medida.
Grabar primero una prueba breve de audio y puntero.
