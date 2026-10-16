"""Descarga puntual del histórico diario de cobre de Cochilco (sin credenciales)."""

import hashlib
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--desde", type=int, default=2010)
    parser.add_argument("--hasta", type=int, default=2013)
    args = parser.parse_args()
    if not 1999 <= args.desde <= args.hasta <= 2025 or args.hasta - args.desde >= 10:
        parser.error("Solicitar un intervalo de hasta diez años, entre 1999 y 2025")
    root = Path(__file__).resolve().parents[2]
    folder = root / "data/raw/cobre_historico"
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / f"cochilco_cobre_bml_{args.desde}_{args.hasta}.xls"
    if output.exists():
        raise FileExistsError(f"No se sobrescribe la fuente existente: {output}")
    url = "https://boletin.cochilco.cl/estadisticas/grafico/crear_excel.asp"
    parameters = dict(
        tipo_metal="Cobre", tipo_consulta="1", bolsa_final="BML",
        dia="1", mes="1", anio=str(args.desde), dia1="31", mes1="12", anio1=str(args.hasta),
        bandera="S",
    )
    request = Request(url, data=urlencode(parameters).encode("ascii"))
    with urlopen(request, timeout=300) as response:
        data = response.read()
        content_type = response.headers.get("Content-Type")
    from src.processing.cobre_historico import Rows
    import re
    rows = Rows()
    rows.feed(data.decode("latin1"))
    dates = [datetime.strptime(r[0], "%d/%m/%Y") for r in rows.rows
             if r and re.fullmatch(r"\d{2}/\d{2}/\d{4}", r[0])]
    if not dates or min(dates).year != args.desde or max(dates).year != args.hasta:
        raise ValueError("La respuesta no cubre ambos años solicitados")
    if len(dates) < 200 * (args.hasta - args.desde + 1):
        raise ValueError("La respuesta contiene menos observaciones de las esperadas")
    output.write_bytes(data)
    metadata = dict(
        source="Comisión Chilena del Cobre (Cochilco)",
        consultation_url="https://boletin.cochilco.cl/estadisticas/grafico.asp?tipo_metal=1",
        download_url=url, method="POST", parameters=parameters,
        downloaded_at_utc=datetime.now(timezone.utc).isoformat(),
        content_type=content_type, original_filename="datos.xls",
        stored_filename=output.name,
        format_note="Exportación original HTML con extensión .xls; no es un XLS binario.",
        sha256=hashlib.sha256(data).hexdigest(),
        unit="Centavos de dólar por libra", frequency="Diaria", market="BML/LME, contado/spot",
        observations=len(dates), first_observation=min(dates).date().isoformat(),
        last_observation=max(dates).date().isoformat(),
    )
    metadata_path = folder / ("procedencia.json" if (args.desde, args.hasta) == (2010, 2013)
                              else f"procedencia_{args.desde}_{args.hasta}.json")
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Descarga conservada: {output} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
