"""Construye una tabla por decisión usando fuentes locales, sin red.

Ejecutar desde la raíz: python -m src.processing.reuniones_tpm
Las fechas provienen de documentos del BCCh; la TPM posterior se obtiene
de la primera observación diaria posterior al anuncio, no del CSV limpio.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MONTHS = {
    month: number for number, month in enumerate(
        ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"], 1
    )
}


def fecha_es(text: str, year: int) -> pd.Timestamp:
    """Último día de un rango: '31 de enero y 1 de febrero 2018' -> 2018-02-01."""
    pairs = re.findall(r"(\d{1,2})\s+de\s+(" + "|".join(MONTHS) + r")", text.lower())
    if not pairs:
        raise ValueError(f"Fecha no reconocida: {text!r}")
    day, month = pairs[-1]
    return pd.Timestamp(year=int(year), month=MONTHS[month], day=int(day))


def leer_fuentes(root: Path) -> pd.DataFrame:
    raw = root / "data/raw/reuniones_tpm"
    records = []
    boletines = json.loads((raw / "rpm_boletines_2010_2012.json").read_text(encoding="utf-8"))
    for row in boletines["registros"]:
        records.append({
            "fecha_decision": fecha_es(row["fecha_texto"], row["anio_boletin"]),
            "fecha_texto_fuente": row["fecha_texto"],
            "fuente_fecha_url": row["fuente_url"],
            "tpm_anunciada_verificada_pct": row["tpm_anunciada_pct"],
            "tipo_reunion": "ordinaria", "nota_fuente": f'Página PDF {row["pagina_pdf"]}',
        })
    complements = json.loads((raw / "rpm_fuentes_complementarias.json").read_text(encoding="utf-8"))
    for group in complements["grupos"]:
        for i, date in enumerate(group["fechas"]):
            announced = group.get("tpm_anunciada_pct")
            if "tpm_anunciadas_pct" in group:
                announced = group["tpm_anunciadas_pct"][i]
            records.append({
                "fecha_decision": pd.Timestamp(date), "fecha_texto_fuente": date,
                "fuente_fecha_url": group["fuente_url"],
                "tpm_anunciada_verificada_pct": announced,
                "tipo_reunion": "ordinaria",
                "nota_fuente": group.get("localizador", group.get("nota", "")),
            })
    archive = json.loads((raw / "rpm_archivo_2015_2025.json").read_text(encoding="utf-8"))
    corrections = {pd.Timestamp(r["fecha_listado"]):r for r in archive["correcciones_verificadas"]}
    additional = {pd.Timestamp(r["fecha_decision"]):r for r in archive["verificaciones_adicionales"]}
    for year, texts in archive["fechas_por_anio"].items():
        for text in texts:
            date = fecha_es(text, int(year))
            correction = corrections.get(date)
            if correction:
                date = pd.Timestamp(correction["fecha_decision"])
            verified = correction or additional.get(date) or {}
            records.append({
                "fecha_decision": date, "fecha_texto_fuente": text,
                "fuente_fecha_url": verified.get("fuente_url", archive["fuente_url"]),
                "tpm_anunciada_verificada_pct": verified.get("tpm_anunciada_pct"),
                "tipo_reunion": "extraordinaria" if "especial" in text else "ordinaria",
                "nota_fuente": correction["nota"] if correction else "",
            })
    meetings = pd.DataFrame(records).sort_values("fecha_decision").reset_index(drop=True)
    if meetings["fecha_decision"].duplicated().any():
        raise ValueError("Fechas de decisión duplicadas en las fuentes")
    if not meetings["fecha_decision"].between("2010-01-01", "2025-12-31").all():
        raise ValueError("Decisión fuera de 2010–2025")
    return meetings


def construir(root: Path = ROOT) -> pd.DataFrame:
    meetings = leer_fuentes(root)
    daily = pd.read_excel(root / "data/raw/tpm_bcentral_diaria.xlsx", sheet_name="Cuadro", header=2)
    daily = daily.iloc[:, :2].set_axis(["fecha", "tpm_pct"], axis=1)
    daily["fecha"] = pd.to_datetime(daily["fecha"], errors="raise")
    daily["tpm_pct"] = pd.to_numeric(daily["tpm_pct"], errors="raise")
    daily = daily.sort_values("fecha").reset_index(drop=True)
    if daily.isna().any().any() or daily["fecha"].duplicated().any():
        raise ValueError("Serie diaria incompleta o con fechas duplicadas")

    # Calendario operativo: fechas efectivamente presentes en la serie oficial.
    # Así se excluyen los fines de semana y feriados sin inventar un calendario L–V.
    previous = daily.rename(columns={"fecha":"fecha_corte", "tpm_pct":"tpm_previa_pct"})
    result = pd.merge_asof(meetings, previous, left_on="fecha_decision", right_on="fecha_corte",
                           direction="backward", allow_exact_matches=False)
    following = daily.rename(columns={"fecha":"fecha_observacion_posterior", "tpm_pct":"tpm_posterior_pct"})
    result = pd.merge_asof(result, following, left_on="fecha_decision", right_on="fecha_observacion_posterior",
                           direction="forward", allow_exact_matches=False)
    required = ["fecha_corte", "tpm_previa_pct", "fecha_observacion_posterior", "tpm_posterior_pct"]
    if result[required].isna().any().any():
        raise ValueError("Falta una observación anterior/posterior para alguna reunión")
    result["variacion_pb"] = ((result["tpm_posterior_pct"]-result["tpm_previa_pct"])*100).round(6)
    result["decision"] = result["variacion_pb"].map(lambda x:"sube" if x>0 else "baja" if x<0 else "mantiene")
    verified = result["tpm_anunciada_verificada_pct"].notna()
    errors = result.loc[verified & (result["tpm_anunciada_verificada_pct"]-result["tpm_posterior_pct"]).abs().gt(1e-8)]
    if not errors.empty:
        raise ValueError("TPM posterior difiere del comunicado:\n"+errors.to_string(index=False))

    # Cada cambio de la serie debe corresponder a exactamente una decisión.
    daily["cambio"] = daily["tpm_pct"].diff().abs().gt(1e-8)
    changes = daily.loc[daily["cambio"] & daily["fecha"].between("2010-01-01","2025-12-31")]
    matched = []
    for change in changes.itertuples(index=False):
        candidates = result.loc[(result["fecha_corte"] < change.fecha)
                                & (change.fecha <= result["fecha_observacion_posterior"])
                                & (result["decision"] != "mantiene")
                                & (result["tpm_posterior_pct"]-change.tpm_pct).abs().lt(1e-8)]
        if len(candidates) != 1:
            raise ValueError(f"Cambio diario sin correspondencia única: {change.fecha.date()} / {change.tpm_pct}")
        matched.append(int(candidates.index[0]))
    if len(set(matched)) != int(result["decision"].ne("mantiene").sum()):
        raise ValueError("Hay decisiones con cambio que no corresponden a un cambio diario")
    if not (result["fecha_corte"] < result["fecha_decision"]).all():
        raise ValueError("Corte de información inválido")
    if not ((result["fecha_decision"]-result["fecha_corte"]).dt.days <= 5).all():
        raise ValueError("Calendario diario tiene una brecha inesperada antes de una reunión")
    if not ((result["fecha_observacion_posterior"]-result["fecha_decision"]).dt.days <= 5).all():
        raise ValueError("Calendario diario tiene una brecha inesperada después de una reunión")
    result["contraste_tpm"] = verified.map({True:"coincide_con_documento",False:"derivada_de_serie_diaria"})
    result["regla_corte"] = "cierre_dia_habil_anterior_America_Santiago"
    result["calendario_corte"] = "fechas_observadas_en_TPM_diaria_BCCh"
    return result


def main() -> None:
    result = construir()
    target = ROOT / "data/processed/reuniones_tpm_2010_2025.csv"
    result.to_csv(target, index=False, date_format="%Y-%m-%d", encoding="utf-8")
    print(f"Generado: {target}")
    print(result.groupby([result["fecha_decision"].dt.year, "decision"]).size().unstack(fill_value=0).to_string())
    print("Total:", len(result), result["decision"].value_counts().to_dict())
    print("Contraste documental de niveles:", result["contraste_tpm"].value_counts().to_dict())


if __name__ == "__main__":
    main()
