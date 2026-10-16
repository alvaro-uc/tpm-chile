"""Recupera el tramo faltante y compara fuentes sin empalmarlas automáticamente."""

import hashlib
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


class Rows(HTMLParser):
    """Lee las celdas de la exportación HTML que Cochilco entrega como XLS."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.row, self.cell = [], [], None

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "tr":
            self.row = []
        elif tag.lower() in ("td", "th"):
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag.lower() in ("td", "th") and self.cell is not None:
            self.row.append("".join(self.cell).strip())
            self.cell = None
        elif tag.lower() == "tr":
            self.rows.append(self.row)


def validate(frame):
    if frame.empty or frame.fecha.duplicated().any():
        raise ValueError("Serie vacía o fechas duplicadas")
    if frame.cu_usd_lb.isna().any() or not frame.cu_usd_lb.between(0, 20).all():
        raise ValueError("Valores faltantes o incompatibles con dólares por libra")
    return frame.sort_values("fecha").reset_index(drop=True)


def read_cochilco(path):
    parser = Rows()
    parser.feed(Path(path).read_bytes().decode("latin1"))
    values = []
    for row in parser.rows:
        if row and re.fullmatch(r"\d{2}/\d{2}/\d{4}", row[0]):
            if len(row) != 2:
                raise ValueError(f"Fila inesperada: {row}")
            # La fuente expresa centavos de dólar/libra; conversión explícita.
            value = float(row[1].replace(".", "").replace(",", ".")) / 100
            values.append((datetime.strptime(row[0], "%d/%m/%Y"), value))
    return validate(pd.DataFrame(values, columns=["fecha", "cu_usd_lb"]))


def read_bcentral(path):
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        codes = [str(c) for row in book["Series"].values for c in row if c is not None]
        if not any("F019.PPB.PRE.100.D" in c for c in codes):
            raise ValueError("El Excel no identifica la serie diaria esperada")
        values = []
        for row in book["Cuadro"].iter_rows(min_row=4, values_only=True):
            if row[0] is None:
                continue
            if not isinstance(row[0], datetime) or not isinstance(row[1], (int, float)):
                raise ValueError(f"Fecha o valor inesperado en el Excel: {row[:2]}")
            values.append((row[0], row[1]))
    finally:
        book.close()
    return validate(pd.DataFrame(values, columns=["fecha", "cu_usd_lb"]))


def build(root=ROOT):
    root = Path(root)
    source = root / "data/raw/cobre_historico/cochilco_cobre_bml_2010_2013.xls"
    metadata = json.loads(source.with_name("procedencia.json").read_text(encoding="utf-8"))
    if hashlib.sha256(source.read_bytes()).hexdigest() != metadata["sha256"]:
        raise ValueError("La descarga de Cochilco no coincide con su huella registrada")
    cochilco = read_cochilco(source)
    bcentral = read_bcentral(root / "data/raw/cu_usd_lb.xlsx")
    if cochilco.fecha.min() != pd.Timestamp("2010-01-04") or cochilco.fecha.max() != pd.Timestamp("2013-12-31"):
        raise ValueError("La descarga de Cochilco no cubre el intervalo esperado")
    missing = cochilco.loc[cochilco.fecha.between("2010-01-01", bcentral.fecha.min() - pd.Timedelta(days=1))].copy()
    comparison = bcentral.merge(cochilco, on="fecha", suffixes=("_bcentral", "_cochilco"), validate="one_to_one")
    if len(comparison) < 250:
        raise ValueError("Solapamiento insuficiente para comparar las fuentes")
    comparison["diferencia_usd_lb"] = comparison.cu_usd_lb_cochilco - comparison.cu_usd_lb_bcentral
    # BCCh tiene dos decimales en este tramo. Media unidad de redondeo: 0,005.
    comparison["compatible_solo_redondeo"] = comparison.diferencia_usd_lb.abs().le(0.005 + 1e-10)
    for frame in (cochilco, missing):
        frame["fuente"] = "Cochilco"
        frame["serie_origen"] = "Cobre BML, consulta diaria"
        frame["unidad"] = "USD/libra"
    delta = comparison.diferencia_usd_lb.abs()
    summary = {
        "cochilco_observaciones": len(cochilco),
        "faltante_recuperado_observaciones": len(missing),
        "faltante_desde": str(missing.fecha.min().date()),
        "faltante_hasta": str(missing.fecha.max().date()),
        "primera_observacion_bcentral": str(bcentral.fecha.min().date()),
        "comparacion_observaciones": len(comparison),
        "comparacion_desde": str(comparison.fecha.min().date()),
        "comparacion_hasta": str(comparison.fecha.max().date()),
        "diferencia_absoluta_media_usd_lb": float(delta.mean()),
        "diferencia_absoluta_maxima_usd_lb": float(delta.max()),
        "coinciden_dentro_redondeo": int(comparison.compatible_solo_redondeo.sum()),
        "correlacion": float(comparison.cu_usd_lb_bcentral.corr(comparison.cu_usd_lb_cochilco)),
        "empalme_automatico": False,
        "motivo": "Se recupera la historia, pero las fuentes no coinciden solo por redondeo. Conservar por separado hasta resolver la definición temporal/metodológica.",
    }
    return cochilco, missing, comparison, summary


def main():
    cochilco, missing, comparison, summary = build()
    folder = ROOT / "data/processed"
    folder.mkdir(parents=True, exist_ok=True)
    for filename, frame in (
        ("cobre_cochilco_diario_2010_2013.csv", cochilco),
        ("cu_usd_lb_faltante_2010_2012.csv", missing),
        ("cobre_comparacion_2012_2013.csv", comparison),
    ):
        frame.to_csv(folder / filename, index=False, date_format="%Y-%m-%d", float_format="%.8f")
    (ROOT / "docs/cobre_validacion.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
