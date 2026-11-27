"""Empaqueta como JSON los CSV generados por el notebook final."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTADOS = ROOT / "output/entrega_final/resultados"
BUILD = ROOT / ".build/entrega_final"


def leer(archivo):
    with (RESULTADOS / f"{archivo}.csv").open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    archivos = ["decisiones_por_periodo", "cobertura", "eda_por_clase", "metricas", "sensibilidad_eee"]
    datos = {nombre: leer(nombre) for nombre in archivos}
    ordinarias = [fila for fila in leer("panel_por_reunion") if fila["tipo_reunion"] == "ordinaria"]
    primera_alza = next(i for i, fila in enumerate(ordinarias) if fila["decision"] == "sube")
    campos = ("fecha_decision", "fecha_corte", "tpm_previa_pct", "pb_ultima", "pb_ultimas_3",
              "dolar_ret_20", "decision")
    datos["muestra_entrenamiento"] = [
        {campo: fila[campo] for campo in campos}
        for fila in ordinarias[primera_alza - 1:primera_alza + 2]
    ]
    predicciones = leer("predicciones")
    datos["inicio_prueba"] = [
        {campo: fila[campo] for campo in ("fecha_decision", "n_train")}
        for fila in predicciones[:2]
    ]
    clases = ["baja", "mantiene", "sube"]
    datos["matrices"] = {
        nombre: [[sum(p["real"] == real and p[nombre] == pred for p in predicciones)
                  for pred in clases] for real in clases]
        for nombre in ["Persistencia", "Logística TPM + dólar"]
    }
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "datos.json").write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
