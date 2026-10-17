"""Extrae evidencia local y deriva el guion sincronizado para el video."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.processing.data_unificada import cargar


def xyear(date):
    # Ocho decimales de año superan ampliamente la resolución diaria y caben en Excel.
    return round(date.year + (date.dayofyear - 1) / (366 if date.is_leap_year else 365), 8)


def main():
    import pandas as pd
    meetings, datasets, inventory = cargar(ROOT)
    daily = datasets['tpm_bcentral_diaria']
    daily = daily.loc[daily.en_ventana_2010_2025]
    # Escalones exactos: dos puntos en cada cambio de valor diario.
    points = []
    previous = None
    for row in daily.itertuples():
        if previous is None:
            points.append([xyear(row.fecha), row.tpm_bcentral_diaria])
        elif row.tpm_bcentral_diaria != previous.tpm_bcentral_diaria:
            points.extend([[xyear(row.fecha), previous.tpm_bcentral_diaria],
                           [xyear(row.fecha), row.tpm_bcentral_diaria]])
        previous = row
    points.append([xyear(previous.fecha), previous.tpm_bcentral_diaria])
    sample = daily.loc[daily.fecha.between('2010-04-01', '2010-06-30')]
    sample_points = []
    previous = None
    for row in sample.itertuples():
        if previous is not None and row.tpm_bcentral_diaria != previous.tpm_bcentral_diaria:
            sample_points.append([row.fecha.dayofyear, previous.tpm_bcentral_diaria])
        sample_points.append([row.fecha.dayofyear, row.tpm_bcentral_diaria])
        previous = row
    decision_points = {key: [[xyear(r.fecha_decision), r.tpm_posterior_pct]
                            for r in meetings.loc[meetings.decision.eq(key)].itertuples()]
                       for key in ['sube', 'baja']}
    counts = meetings.decision.value_counts().to_dict()
    assert counts == {'mantiene': 103, 'baja': 31, 'sube': 27}
    payload = dict(counts=counts, total=len(meetings), daily=points, sample=sample_points,
                   decision_points=decision_points, cobre_filas=len(datasets['cu_usd_lb']),
                   inventory=inventory.to_dict('records'))
    build = ROOT / '.build/presentacion'
    build.mkdir(parents=True, exist_ok=True)
    (build / 'datos.json').write_text(json.dumps(payload, default=str, ensure_ascii=False), encoding='utf-8')
    print(f'{len(meetings)} decisiones, {len(points)} puntos de escalón, {len(sample_points)} puntos de ejemplo')


if __name__ == '__main__':
    main()
