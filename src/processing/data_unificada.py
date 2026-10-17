"""Integración auditable por reunión. No infiere publicaciones desde períodos."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INICIO = pd.Timestamp('2010-01-01')
FIN = pd.Timestamp('2025-12-31')
INICIO_ANTECEDENTES = pd.Timestamp('2009-01-01')
# variable, archivo, frecuencia, unidad, descripción
SERIES = [
    ("tpm_bcentral_diaria", "tpm_bcentral_diaria_clean.csv", "diaria", "%", "TPM vigente; contrastar con tpm_previa_pct, no con el resultado."),
    ("clp_usd", "clp_usd_clean.csv", "diaria", "CLP/USD", "Dólar observado; operaciones del día bancario previo a su publicación."),
    ("cu_usd_lb", "cobre_cochilco_diario_2010_2025.csv", "diaria", "USD/libra", "Cobre spot BML/LME de Cochilco; fuente única 2010–2025."),
    ("desempleo_total_mensual", "desempleo_total_mensual_clean.csv", "mensual", "%", "Desocupación INE, trimestre móvil; validar mes de referencia y revisiones."),
    ("exp_tpm_mensual_mediana", "exp_tpm_mensual_mediana_clean.csv", "mensual", "%", "EEE: mediana de TPM esperada en el mes; verificar publicación de cada encuesta."),
    ("imacec_empalmado_original", "imacec_empalmado_original_clean.csv", "mensual", "2018=100", "IMACEC original empalmado: nivel, no crecimiento; sujeto a revisiones."),
    ("ipc_general_mensual", "ipc_general_mensual_clean.csv", "mensual", "%", "Variación mensual del IPC; no es el nivel del índice."),
    ("ipc_general_anual", "ipc_general_anual_clean.csv", "anual", "%", "Variación anual histórica de diciembre: NO es inflación interanual mensual."),
]


def cargar(root=ROOT):
    """Ventana 2010–2025 y reserva técnica 2009; originales intactos."""
    folder = root / "data/processed"
    paths = [folder / "reuniones_tpm_2010_2025_clean.csv", folder / "reuniones_tpm_2010_2025.csv"]
    existing = [p for p in paths if p.exists()]
    if not existing:
        raise FileNotFoundError("Regenerar reuniones con python -m src.processing.reuniones_tpm")
    meetings = pd.read_csv(existing[0], parse_dates=["fecha_decision", "fecha_corte"])
    if len(existing) == 2:
        other = pd.read_csv(existing[1])
        cols = ["fecha_decision", "fecha_corte", "decision", "tpm_previa_pct"]
        pd.testing.assert_frame_equal(meetings[cols].astype(str).reset_index(drop=True),
                                      other[cols].astype(str).reset_index(drop=True))
    meetings = meetings.loc[meetings.fecha_decision.between(INICIO, FIN)].sort_values("fecha_decision").reset_index(drop=True)
    if meetings.fecha_decision.isna().any() or meetings.fecha_decision.duplicated().any():
        raise ValueError("Fechas de reunión ausentes o duplicadas")
    if not (meetings.fecha_corte < meetings.fecha_decision).all():
        raise ValueError("Corte ausente o posterior/igual a decisión")
    meetings.insert(0, "id_reunion", "RPM_" + meetings.fecha_decision.dt.strftime("%Y%m%d"))
    datasets, inventory = {}, []
    for var, filename, freq, unit, description in SERIES:
        df = pd.read_csv(folder / filename, parse_dates=["fecha"])
        df[var] = pd.to_numeric(df[var], errors="raise")
        if df[["fecha", var]].isna().any().any() or df.fecha.duplicated().any():
            raise ValueError(f"Fechas duplicadas o faltantes en {var}")
        original_rows, original_start, original_end = len(df), df.fecha.min(), df.fecha.max()
        df = df.loc[df.fecha.between(INICIO_ANTECEDENTES, FIN)].copy()
        df = df.sort_values("fecha").reset_index(drop=True)
        df.insert(0, "id_observacion", var + "_" + df.fecha.dt.strftime("%Y%m%d"))
        df['en_ventana_2010_2025'] = df.fecha.between(INICIO, FIN)
        datasets[var] = df
        inventory.append(dict(variable=var, archivo=filename, frecuencia=freq, unidad=unit,
                              descripcion=description, filas_originales=original_rows,
                              inicio_original=original_start, fin_original=original_end,
                              filas_2010_2025=int(df.en_ventana_2010_2025.sum()),
                              antecedentes_2009=int((~df.en_ventana_2010_2025).sum()),
                              filas=len(df), inicio=df.fecha.min(), fin=df.fecha.max()))
    return meetings, datasets, pd.DataFrame(inventory)


CAPTURA = ["id_observacion", "variable", "fecha_referencia", "valor_descargado",
           "fecha_disponible", "valor_publicado", "fuente_publicacion", "evidencia_version", "nota"]


def plantilla_publicaciones(datasets):
    """Una fila por observación; completar con evidencia, nunca con rezagos inventados."""
    parts = []
    for var, df in datasets.items():
        part = df[["id_observacion", "fecha", var]].rename(columns={"fecha": "fecha_referencia", var: "valor_descargado"})
        part = part.loc[part.fecha_referencia.between(INICIO_ANTECEDENTES, FIN)].copy()
        part["variable"] = var
        for col in CAPTURA:
            if col not in part:
                part[col] = pd.NA
        parts.append(part[CAPTURA])
    return pd.concat(parts, ignore_index=True)


def preparar_captura(root, datasets):
    """Recorta cola sin borrar evidencia manual e incorpora el ejemplo oficial."""
    out = root / 'data/processed/unificada'
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'publicaciones_por_documentar.csv'
    template = plantilla_publicaciones(datasets)
    fields = ['fecha_disponible', 'valor_publicado', 'fuente_publicacion', 'evidencia_version', 'nota']
    existing = pd.read_csv(path, dtype=object) if path.exists() else template.astype(object)
    in_scope = existing.id_observacion.isin(template.id_observacion)
    if existing.loc[~in_scope, fields].notna().any().any():
        raise ValueError('Hay evidencia fuera de la ventana; conservarla y revisar antes de recortar')
    existing = existing.loc[in_scope].copy()
    missing = template.loc[~template.id_observacion.isin(existing.id_observacion)]
    existing = pd.concat([existing, missing], ignore_index=True).astype(object)
    seed = pd.read_csv(root / 'data/raw/publicaciones_indicadores/ipc_ejemplo_2024.csv', dtype=object)
    for record in seed.to_dict('records'):
        target = existing.id_observacion.eq(record['id_observacion'])
        empty = existing.loc[target, fields].isna().all(axis=1)
        indices = empty.index[empty]
        for field in fields:
            existing.loc[indices, field] = record[field]
    existing.to_csv(path, index=False, date_format='%Y-%m-%d')
    coverage = pd.read_csv(root / 'data/raw/publicaciones_indicadores/cobertura_ejemplo.csv')
    return existing, coverage


def validar_publicaciones(publications, datasets):
    """Admite varias versiones; exige valor histórico y evidencia para cada una."""
    required = ["id_observacion", "variable", "fecha_disponible", "valor_publicado",
                "fuente_publicacion", "evidencia_version"]
    if not set(required).issubset(publications.columns):
        raise ValueError(f"Columnas requeridas: {required}")
    p = publications.copy()
    touched = p[required[2:]].replace(r"^\s*$", pd.NA, regex=True).notna().any(axis=1)
    p = p.loc[touched, required].copy()
    if p.empty:
        return pd.DataFrame(columns=required + ["fecha_referencia"])
    if p.replace(r"^\s*$", pd.NA, regex=True).isna().any().any():
        raise ValueError("Publicación incompleta: faltan fecha, valor o evidencias")
    p["fecha_disponible"] = pd.to_datetime(p.fecha_disponible, errors="raise")
    if not p.fecha_disponible.eq(p.fecha_disponible.dt.normalize()).all():
        raise ValueError("Usar fechas locales de disponibilidad, sin horas")
    p["valor_publicado"] = pd.to_numeric(p.valor_publicado, errors="raise")
    if p.duplicated(["id_observacion", "fecha_disponible"]).any():
        raise ValueError("Versiones ambiguas en el mismo día")
    catalog = pd.concat([df[["id_observacion", "fecha"]].assign(variable=var)
                         for var, df in datasets.items()], ignore_index=True)
    p = p.merge(catalog, on=["id_observacion", "variable"], how="left", validate="many_to_one")
    if p.fecha.isna().any():
        raise ValueError("Observación o variable desconocida")
    return p.rename(columns={"fecha": "fecha_referencia"})


def vincular(meetings, datasets, publications, cobertura=None):
    """Panel largo: 1 reunión × 1 variable; elige período y versión disponibles."""
    p = validar_publicaciones(publications, datasets)
    if cobertura is not None:
        cobertura = cobertura.copy()
        for col in ['inicio', 'fin']:
            cobertura[col] = pd.to_datetime(cobertura[col], errors='raise')
        if not cobertura.inicio.le(cobertura.fin).all():
            raise ValueError('Intervalo de cobertura invertido')
    records = []
    for meeting in meetings.itertuples():
        for var, df in datasets.items():
            # Esta selección solo diagnostica el riesgo de unir por referencia.
            candidates = df.loc[df.fecha.le(meeting.fecha_corte)]
            candidate = candidates.iloc[-1] if len(candidates) else None
            available = p.loc[p.variable.eq(var) & p.fecha_disponible.le(meeting.fecha_corte)]
            cubierto = cobertura is None or (
                cobertura.variable.eq(var) & cobertura.inicio.le(meeting.fecha_corte)
                & cobertura.fin.ge(meeting.fecha_corte)).any()
            if not cubierto:
                available = available.iloc[:0]
            # Un release tardío de un período antiguo no desplaza un período reciente.
            available = available.sort_values(["fecha_referencia", "fecha_disponible"])
            chosen = available.iloc[-1] if len(available) else None
            record = dict(id_reunion=meeting.id_reunion, fecha_decision=meeting.fecha_decision,
                          fecha_corte=meeting.fecha_corte, variable=var,
                          estado="disponibilidad_y_version_documentadas" if chosen is not None else "pendiente_evidencia",
                          calendario_documentado=bool(cobertura is not None and cubierto),
                          id_observacion=pd.NA, fecha_referencia=pd.NaT, fecha_disponible=pd.NaT,
                          valor=pd.NA, fuente_publicacion=pd.NA, evidencia_version=pd.NA,
                          candidato_id=pd.NA, candidato_fecha=pd.NaT, candidato_valor=pd.NA)
            if candidate is not None:
                record.update(candidato_id=candidate.id_observacion, candidato_fecha=candidate.fecha,
                              candidato_valor=candidate[var])
            if chosen is not None:
                for col in ["id_observacion", "fecha_referencia", "fecha_disponible", "fuente_publicacion", "evidencia_version"]:
                    record[col] = chosen[col]
                record["valor"] = chosen.valor_publicado
            records.append(record)
    links = pd.DataFrame(records)
    for col in ["fecha_referencia", "fecha_disponible", "candidato_fecha"]:
        links[col] = pd.to_datetime(links[col])
    links["dias_desde_publicacion"] = (links.fecha_corte - links.fecha_disponible).dt.days
    links["dias_desde_referencia"] = (links.fecha_corte - links.fecha_referencia).dt.days
    links["candidato_en_fecha_corte"] = links.candidato_fecha.eq(links.fecha_corte)
    assert not links.duplicated(["id_reunion", "variable"]).any()
    assert links.fecha_disponible.dropna().le(links.loc[links.fecha_disponible.notna(), "fecha_corte"]).all()
    wide = links.pivot(index="id_reunion", columns="variable", values="valor").reset_index()
    # Lista explícita: no trasladar niveles posteriores ni variación a predictores.
    unified = meetings[["id_reunion", "fecha_decision", "fecha_corte", "tipo_reunion", "decision"]].merge(
        wide, on="id_reunion", validate="one_to_one")
    variables = [s[0] for s in SERIES]
    unified["n_variables_disponibles"] = unified[variables].notna().sum(axis=1)
    unified["lista_para_modelo"] = unified.n_variables_disponibles.eq(len(variables))
    calendar_ok = links.groupby('id_reunion').calendario_documentado.all()
    unified['lista_para_modelo'] &= unified.id_reunion.map(calendar_ok)
    return links, unified


def exportar(root, meetings, datasets, publications, cobertura=None):
    links, unified = vincular(meetings, datasets, publications, cobertura)
    out = root / "data/processed/unificada"
    out.mkdir(parents=True, exist_ok=True)
    links.to_csv(out / "vinculos_reunion_variable.csv", index=False, date_format="%Y-%m-%d")
    unified.to_csv(out / "tpm_indicadores_disponibles.csv", index=False, date_format="%Y-%m-%d")
    for var, df in datasets.items():
        # Una observación puede aparecer en varios vínculos: relación muchos-a-uno.
        links.loc[links.variable.eq(var)].to_csv(out / f"asignacion_{var}.csv", index=False, date_format="%Y-%m-%d")
        df.loc[df.en_ventana_2010_2025].to_csv(out / f'serie_{var}_2010_2025.csv', index=False, date_format='%Y-%m-%d')
        df.loc[~df.en_ventana_2010_2025].to_csv(out / f'antecedentes_2009_{var}.csv', index=False, date_format='%Y-%m-%d')
    return links, unified
