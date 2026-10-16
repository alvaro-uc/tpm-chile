# Ingesta

Para cobre se autorizó la descarga puntual de Cochilco para 2010–2025.
`descargar_cobre_cochilco` conserva originales y procedencia; sus opciones
`--desde` y `--hasta` permiten solicitudes de hasta diez años. No sobrescribe
descargas existentes. El procesamiento habitual lee esos archivos localmente;
ver `data/raw/cobre_historico/README.md`.

Leer los archivos fuente locales versionados en `data/raw/`. Para la TPM, la entrada es `tpm_bcentral_diaria.xlsx`; mantener la descarga original intacta y cargar desde la hoja y columnas documentadas en `docs/README.md`. El procesamiento ordinario no usa APIs ni descargas automáticas. Para el historial de reuniones se autorizó una recopilación puntual desde páginas y documentos oficiales; las fechas, extractos y fuentes se conservan localmente en `data/raw/reuniones_tpm/`. Ver `docs/reuniones_tpm.md` y el notebook `notebooks/02_reuniones_tpm.ipynb`.
