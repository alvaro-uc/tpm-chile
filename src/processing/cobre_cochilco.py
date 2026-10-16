"""Construye la serie oficial de cobre elegida para el proyecto: Cochilco 2010–2025.

Procesamiento local, sin red y sin empalmar precios del Banco Central.
"""

import hashlib
import json
from pathlib import Path

import pandas as pd

from src.processing.cobre_historico import ROOT, read_cochilco, validate

SOURCES = (
    ("cochilco_cobre_bml_2010_2013.xls", "procedencia.json"),
    ("cochilco_cobre_bml_2013_2019.xls", "procedencia_2013_2019.json"),
    ("cochilco_cobre_bml_2019_2025.xls", "procedencia_2019_2025.json"),
)


def combine(parts):
    combined = pd.concat(parts, ignore_index=True)
    duplicate = combined[combined.duplicated("fecha", keep=False)]
    if not duplicate.empty:
        spread = duplicate.groupby("fecha").cu_usd_lb.agg(lambda s: s.max() - s.min())
        if (spread > 1e-12).any():
            raise ValueError(f"Precios contradictorios entre descargas: {spread[spread > 1e-12].index.tolist()}")
    # En un solapamiento idéntico se conserva la descarga más antigua.
    return validate(combined.drop_duplicates("fecha", keep="first")), len(combined) - combined.fecha.nunique()


def build(root=ROOT):
    root = Path(root)
    folder = root / "data/raw/cobre_historico"
    parts, sources = [], []
    for filename, metadata_filename in SOURCES:
        path = folder / filename
        metadata = json.loads((folder / metadata_filename).read_text(encoding="utf-8"))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != metadata["sha256"]:
            raise ValueError(f"Fuente alterada: {filename}")
        parameters = metadata["parameters"]
        if (parameters["tipo_metal"], parameters["tipo_consulta"], parameters["bolsa_final"]) != ("Cobre", "1", "BML"):
            raise ValueError(f"Metal, frecuencia o bolsa inesperados: {filename}")
        frame = read_cochilco(path)
        if frame.fecha.min().year != int(parameters["anio"]) or frame.fecha.max().year != int(parameters["anio1"]):
            raise ValueError(f"Cobertura distinta de la solicitada: {filename}")
        frame["archivo_origen"] = filename
        parts.append(frame)
        sources.append(dict(archivo=filename, sha256=digest, observaciones=len(frame)))
    frame, duplicate_count = combine(parts)
    frame = frame.loc[frame.fecha.between("2010-01-01", "2025-12-31")].copy()
    if not frame.cu_usd_lb.gt(0).all():
        raise ValueError("Se esperaba un precio estrictamente positivo")
    if frame.fecha.min() > pd.Timestamp("2010-01-08") or frame.fecha.max() < pd.Timestamp("2025-12-24"):
        raise ValueError("Falta un extremo del período analítico")
    months = frame.groupby(frame.fecha.dt.to_period("M")).size()
    expected = pd.period_range("2010-01", "2025-12", freq="M")
    if not months.index.equals(expected) or months.min() < 15:
        raise ValueError("Mes ausente o con cobertura anormalmente baja")
    annual_counts = frame.groupby(frame.fecha.dt.year).size()
    if annual_counts.min() < 230:
        raise ValueError("Año con cobertura anormalmente baja")
    frame["fuente"] = "Cochilco"
    frame["mercado"] = "BML/LME spot"
    frame["unidad"] = "USD/libra"
    frame = frame[["fecha", "cu_usd_lb", "fuente", "mercado", "unidad", "archivo_origen"]]
    # Es un inventario para revisión; no se supone que todo lunes-viernes cotice.
    weekdays = pd.bdate_range("2010-01-01", "2025-12-31")
    absent = pd.DataFrame({"fecha": weekdays.difference(frame.fecha)})
    absent["estado"] = "Sin observación en la fuente; revisar calendario, no imputado"
    summary = dict(
        fuente_elegida="Cochilco", mercado="BML/LME spot", unidad="USD/libra",
        periodo_proyecto="2010–2025", observaciones=len(frame),
        primera_fecha=frame.fecha.min().date().isoformat(), ultima_fecha=frame.fecha.max().date().isoformat(),
        meses_cubiertos=len(months), duplicados_identicos_eliminados=int(duplicate_count),
        observaciones_por_anio={str(k): int(v) for k, v in annual_counts.items()},
        dias_lunes_viernes_sin_observacion=len(absent),
        observaciones_fin_de_semana=int(frame.fecha.dt.dayofweek.ge(5).sum()),
        precio_minimo_usd_lb=float(frame.cu_usd_lb.min()), precio_maximo_usd_lb=float(frame.cu_usd_lb.max()),
        mezcla_con_bcentral=False, interpolacion=False, relleno_de_fechas=False,
        fecha_significado="Fecha de cotización informada por la fuente; no certifica hora de publicación.",
        archivos_fuente=sources,
    )
    return frame, absent, summary


def main():
    frame, absent, summary = build()
    folder = ROOT / "data/processed"
    folder.mkdir(parents=True, exist_ok=True)
    frame.to_csv(folder / "cobre_cochilco_diario_2010_2025.csv", index=False, date_format="%Y-%m-%d", float_format="%.4f")
    absent.to_csv(folder / "cobre_cochilco_calendario_sin_observacion_2010_2025.csv", index=False, date_format="%Y-%m-%d")
    (ROOT / "docs/cobre_cochilco_validacion.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
