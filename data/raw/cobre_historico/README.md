# Recuperación del histórico diario del cobre

**Decisión del 16-10-2026:** Cochilco será la fuente única de cobre spot BML/LME
para el período del proyecto 2010–2025. No se empalma con la serie BCCh.

Además de la descarga inicial 2010–2013, esta carpeta contiene:

- `cochilco_cobre_bml_2013_2019.xls` y `procedencia_2013_2019.json`.
- `cochilco_cobre_bml_2019_2025.xls` y `procedencia_2019_2025.json`.

Los solapamientos en 2013 y 2019 permiten comprobar que los precios coincidan
entre descargas. Los JSON registran el POST, parámetros, unidad, fecha UTC,
extremos, recuento y SHA-256 de cada nueva respuesta original.

La tabla elegida para análisis es
`data/processed/cobre_cochilco_diario_2010_2025.csv`. Se genera localmente con:

```powershell
python -m src.processing.cobre_cochilco
```

Consulta puntual realizada el 16 de octubre de 2026. Se conserva la respuesta
original de Cochilco sin editar, además de los parámetros, fecha UTC y SHA-256
en `procedencia.json`.

- `cochilco_cobre_bml_2010_2013.xls`: exportación de **Cobre, diaria, BML**,
  del 01-01-2010 al 31-12-2013; 1.009 observaciones efectivamente publicadas.
  El servidor la entrega como `datos.xls`, pero su contenido es una tabla HTML,
  no un libro XLS binario. No abrirla con `openpyxl`; el procesador lee su HTML.
- La unidad de origen es **centavos de dólar por libra**. El procesamiento
  divide por 100 para obtener USD/libra. No hay conversión de moneda ni ajuste
  estimado para acercar los precios a la otra fuente.
- Se solicitó hasta 2013 para comparar con el Excel del Banco Central en un
  intervalo común. El suplemento faltante termina el 04-10-2012.

## Fuentes

1. [Cochilco: consulta de precios de los metales](https://boletin.cochilco.cl/estadisticas/grafico.asp?tipo_metal=1).
   Seleccionar Cobre, Diaria, BML/LME y el intervalo indicado. El enlace de
   exportación realiza un POST a `grafico/crear_excel.asp`; un GET no reproduce
   la consulta y puede devolver datos por defecto. La respuesta puede demorar
   varios minutos.
2. [Cochilco, tabla 2.2, enero de 2010](https://boletin.cochilco.cl/productos/boletin.asp?anio=2010&mes=01&tabla=tabla2_2).
   Distingue explícitamente contado/spot de futuros y BML de COMEX. El spot BML
   del 04-01-2010 es 338,561 centavos/libra; la exportación entrega 338,56.
3. [Buscador BCCh, serie F019.PPB.PRE.100.D](https://si3.bcentral.cl/Search/Buscar/Index/?st=F019.PPB.PRE.100.D&Idioma=ES).
   Registra primera observación el **05-10-2012**. El buscador presenta un rótulo
   inconsistente sobre onzas troy; se usa la definición y unidad del Excel
   original y del cuadro diario BDE: cobre refinado BML, dólares/libra.
4. [Cuadro diario de productos básicos BDE](https://si3.bcentral.cl/Siete/ES/Siete/Cuadro/CAP_EI/MN_EI11/EI_PROD_BAS_DIARIO/638358101053598187).
   La fila de cobre está vacía en 2010 y antes de octubre de 2012.

## Reproducción

El procesamiento de la serie elegida no usa red:

```powershell
python -m src.processing.cobre_cochilco
```

La comparación inicial con BCCh se puede regenerar por separado con
`python -m src.processing.cobre_historico`.

Para repetir específicamente la descarga desde el servidor oficial, conservando
antes una copia de esta carpeta fuera de su ruta de destino:

```powershell
python -m src.ingest.descargar_cobre_cochilco
python -m src.ingest.descargar_cobre_cochilco --desde 2013 --hasta 2019
python -m src.ingest.descargar_cobre_cochilco --desde 2019 --hasta 2025
```

El descargador se niega a sobrescribir un archivo existente. La descarga puntual
fue autorizada para recuperar la historia; no se añade una dependencia de red al
análisis habitual. No se necesitan credenciales ni se consulta una API privada.

**Estado:** se adopta Cochilco para todo 2010–2025; se conserva la investigación
de discrepancias con BCCh como auditoría. Ver `docs/cobre_historico.md` y el
notebook `03_cobre_historico.ipynb`. No se modificó `data/raw/cu_usd_lb.xlsx`.
