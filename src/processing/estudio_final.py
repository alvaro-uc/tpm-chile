"""Panel y evaluación cronológica para la entrega final de IMT2200."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.processing import data_unificada, reuniones_tpm

ROOT = Path(__file__).resolve().parents[2]
CLASES = ["baja", "mantiene", "sube"]
COLORES = {"baja": "#16765B", "mantiene": "#2364AA", "sube": "#B63F45"}
N_INICIAL = 60
MODELOS_PRINCIPALES = ["Mayoría histórica", "Persistencia", "Logística TPM", "Logística TPM + dólar"]
MODELO_RETROSPECTIVO = "Logística TPM + macro retrospectiva"
ESTADO = ["tpm_previa_pct", "pb_ultima", "pb_ultimas_3"]
DOLAR = ["dolar_ret_20"]
MACRO = ["ipc_12m", "imacec_12m", "desemp_12m", "cobre_ret_20"]
EDA = {
    "ipc_12m": ("IPC acumulado a 12 meses", "%"),
    "imacec_12m": ("IMACEC original interanual", "%"),
    "desemp_12m": ("Cambio interanual del desempleo", "pp"),
    "dolar_ret_20": ("Dólar observado a 20 cotizaciones", "%"),
    "cobre_ret_20": ("Cobre BML a 20 cotizaciones", "%"),
    "eee_brecha": ("Expectativa EEE anterior menos TPM", "pp"),
}
PERIODOS = ["2010–13", "2014–17", "2018–21", "2022–25"]
FX_FICHA = (
    "https://www.bcentral.cl/documents/33528/2546026/Dolar_Observado.pdf/"
    "d8d86d97-9939-b71e-1d93-afe4eab3f743?t=1707422015118"
)


def alinear(serie, corte, *, dias_max, periodo_meses=None, estricto=False):
    """Devuelve fecha y valor por corte, sin rellenar valores demasiado antiguos."""
    limite = corte if periodo_meses is None else corte.dt.to_period("M").dt.to_timestamp() - pd.DateOffset(months=periodo_meses)
    fechas = serie.index.searchsorted(limite, side="left" if estricto else "right") - 1
    validas = fechas >= 0
    salida = pd.DataFrame(index=corte.index)
    salida["fecha"] = serie.index.take(fechas.clip(min=0)).where(validas)
    salida["edad"] = (corte - salida.fecha).dt.days
    valores = serie.to_numpy()[fechas.clip(min=0)]
    salida["valor"] = np.where(validas & salida.edad.le(dias_max), valores, np.nan)
    return salida


def agregar(panel, nombre, serie, **regla):
    asignacion = alinear(serie, panel.fecha_corte, **regla)
    panel[nombre] = asignacion.valor
    panel[nombre + "_referencia"] = asignacion.fecha
    panel[nombre + "_edad_dias"] = asignacion.edad


def construir_panel(root=ROOT):
    """Verifica el registro anterior y arma una fila por anuncio con trazabilidad."""
    reuniones, fuentes, inventario = data_unificada.cargar(root)
    oficial = reuniones_tpm.construir(root)
    campos = ["fecha_decision", "fecha_corte", "decision", "tpm_previa_pct", "variacion_pb"]
    pd.testing.assert_frame_equal(reuniones[campos], oficial[campos], check_dtype=False)
    publicaciones, cobertura = data_unificada.preparar_captura(root, fuentes)
    vinculos, _ = data_unificada.vincular(reuniones, fuentes, publicaciones, cobertura)
    panel = reuniones[["id_reunion", "fecha_decision", "fecha_corte", "tipo_reunion",
                       "tpm_previa_pct", "variacion_pb", "decision"]].copy()

    series = {nombre: tabla.set_index("fecha")[nombre] for nombre, tabla in fuentes.items()}
    usd = series["clp_usd"]
    corte_usd = alinear(usd, panel.fecha_decision, dias_max=10, estricto=True)
    panel["corte_contraste_usd"] = corte_usd.fecha
    panel["corte_coincide_usd"] = panel.fecha_corte.eq(corte_usd.fecha)

    anterior = panel.variacion_pb.shift()
    panel["decision_anterior"] = panel.decision.shift()
    panel["fecha_ultimo_anuncio"] = panel.fecha_decision.shift()
    panel["pb_ultima"] = anterior
    panel["pb_ultimas_3"] = anterior.rolling(3, min_periods=3).sum()
    conocidos = panel.fecha_ultimo_anuncio.dropna()
    assert conocidos.le(panel.loc[conocidos.index, "fecha_corte"]).all()

    # Se excluyen dos vigencias de la Circular 802 de la construcción de retornos.
    # El contraste de calendario, arriba, conserva las fechas de la serie original.
    usd = usd.drop(pd.to_datetime(["2018-01-16", "2018-01-17"]), errors="ignore")
    agregar(panel, "dolar_nivel", usd, dias_max=7)
    agregar(panel, "dolar_ret_20", usd.pct_change(20).mul(100), dias_max=7)
    panel["dolar_ret_20_inicio"] = panel.dolar_ret_20_referencia.map(usd.index.to_series().shift(20))

    cobre = series["cu_usd_lb"]
    agregar(panel, "cobre_nivel", cobre, dias_max=10, estricto=True)
    agregar(panel, "cobre_ret_20", cobre.pct_change(20).mul(100), dias_max=10, estricto=True)
    panel["cobre_ret_20_inicio"] = panel.cobre_ret_20_referencia.map(cobre.index.to_series().shift(20))

    ipc = series["ipc_general_mensual"].asfreq("MS")
    imacec = series["imacec_empalmado_original"].asfreq("MS")
    desempleo = series["desempleo_total_mensual"].asfreq("MS")
    agregar(panel, "ipc_mensual", ipc, dias_max=100, periodo_meses=2)
    agregar(panel, "ipc_12m", (1 + ipc / 100).rolling(12).apply(np.prod, raw=True).sub(1).mul(100),
            dias_max=100, periodo_meses=2)
    agregar(panel, "imacec_nivel", imacec, dias_max=130, periodo_meses=3)
    agregar(panel, "imacec_12m", imacec.pct_change(12, fill_method=None).mul(100),
            dias_max=130, periodo_meses=3)
    agregar(panel, "desemp_nivel", desempleo, dias_max=130, periodo_meses=3)
    agregar(panel, "desemp_12m", desempleo.diff(12), dias_max=130, periodo_meses=3)
    agregar(panel, "eee_previa", series["exp_tpm_mensual_mediana"], dias_max=75, periodo_meses=1)
    panel["eee_brecha"] = panel.eee_previa - panel.tpm_previa_pct
    periodo_eee = panel.fecha_corte.dt.to_period("M").dt.to_timestamp()
    periodo_eee = periodo_eee.where(panel.fecha_corte.dt.day.ge(13), periodo_eee - pd.DateOffset(months=1))
    panel["eee_regla_13"] = periodo_eee.map(series["exp_tpm_mensual_mediana"])
    panel["eee_mismo_mes"] = panel.fecha_corte.dt.to_period("M").dt.to_timestamp().map(series["exp_tpm_mensual_mediana"])

    ipc_documentado = vinculos.loc[vinculos.variable.eq("ipc_general_mensual")].set_index("id_reunion")
    for campo in ["fecha_referencia", "fecha_disponible", "fuente_publicacion", "evidencia_version"]:
        panel["ipc_boletin_" + campo] = panel.id_reunion.map(ipc_documentado[campo])
    panel["ipc_boletin_valor"] = pd.to_numeric(panel.id_reunion.map(ipc_documentado.valor))
    panel["periodo"] = pd.cut(panel.fecha_decision.dt.year, [2009, 2013, 2017, 2021, 2025], labels=PERIODOS)
    return panel, vinculos, inventario


def cobertura_panel(panel, inventario):
    """Distingue cantidad de candidatos de cantidad con disponibilidad respaldada."""
    especificacion = [
        ("tpm_bcentral_diaria", "tpm_previa_pct", "fecha_corte", "tpm_previa_pct", "TPM vigente; evitar duplicarla"),
        ("clp_usd", "dolar_ret_20", "dolar_ret_20_referencia", "dolar_ret_20", "Vigencia BCCh; retorno de 20 cotizaciones"),
        ("cu_usd_lb", "cobre_ret_20", "cobre_ret_20_referencia", None, "Fecha de cotización; faltan horas publicadas"),
        ("desempleo_total_mensual", "desemp_12m", "desemp_12m_referencia", None, "Trimestre móvil; versión retrospectiva"),
        ("exp_tpm_mensual_mediana", "eee_brecha", "eee_previa_referencia", None, "Mes previo; horizonte de fin de mes"),
        ("imacec_empalmado_original", "imacec_12m", "imacec_12m_referencia", None, "Índice empalmado; sujeto a revisiones"),
        ("ipc_general_mensual", "ipc_12m", "ipc_12m_referencia", "ipc_boletin_valor", "Boletines solo para el IPC mensual de ejemplo"),
        ("ipc_general_anual", None, None, None, "Diciembre; excluido por frecuencia y redundancia"),
    ]
    resumen = []
    for variable, feature, fecha, respaldado, nota in especificacion:
        observable = panel[feature].notna() if feature else pd.Series(False, index=panel.index)
        edad = (panel.loc[observable, "fecha_corte"] - panel.loc[observable, fecha]).dt.days if fecha else pd.Series(dtype=float)
        resumen.append({
            "variable": variable, "transformacion": feature or "no construida",
            "n_candidato_transformado": int(observable.sum()),
            "n_con_respaldo": int(panel[respaldado].notna().sum()) if respaldado else 0,
            "edad_mediana_dias": edad.median() if not edad.empty else np.nan,
            "edad_max_dias": edad.max() if not edad.empty else np.nan,
            "criterio": nota,
        })
    return inventario[["variable", "frecuencia", "unidad", "filas_2010_2025"]].merge(
        pd.DataFrame(resumen), on="variable", validate="one_to_one"
    )


def estadisticas_eda(panel):
    """Distribuciones en el bloque inicial, antes del período de evaluación."""
    filas = []
    for variable, (nombre, unidad) in EDA.items():
        for clase in CLASES:
            s = panel.loc[panel.decision.eq(clase), variable].dropna()
            filas.append({
                "variable": variable, "nombre": nombre, "unidad": unidad, "decision": clase,
                "n": len(s), "mediana": s.median(), "q25": s.quantile(.25), "q75": s.quantile(.75),
            })
    return pd.DataFrame(filas)


def evaluar(ordinarias):
    """Una predicción por reunión futura con hiperparámetros fijos y ventana creciente."""
    from sklearn.dummy import DummyClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    modelos = {
        "Logística TPM": ESTADO,
        "Logística TPM + dólar": ESTADO + DOLAR,
        MODELO_RETROSPECTIVO: ESTADO + DOLAR + MACRO,
    }
    assert ordinarias.fecha_decision.is_monotonic_increasing
    assert ordinarias.iloc[N_INICIAL:][ESTADO + DOLAR].notna().all().all()
    resultados = []
    for i in range(N_INICIAL, len(ordinarias)):
        train = ordinarias.iloc[:i]
        test = ordinarias.iloc[[i]]
        fila = test.iloc[0]
        y = train.decision
        assert len(y.unique()) == len(CLASES) and train.fecha_decision.max() <= fila.fecha_corte
        dummy_x = np.zeros((len(train), 1))
        base = DummyClassifier(strategy="most_frequent").fit(dummy_x, y)
        pred = {
            "Mayoría histórica": base.predict([[0]])[0],
            "Persistencia": fila.decision_anterior,
        }
        probabilidades = {}
        for nombre, cols in modelos.items():
            modelo = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                   LogisticRegression(C=1.0, max_iter=500))
            modelo.fit(train[cols], y)
            pred[nombre] = modelo.predict(test[cols])[0]
            if nombre == "Logística TPM + dólar":
                probabilidades = dict(zip(modelo.classes_, modelo.predict_proba(test[cols])[0]))
        resultados.append({
            "id_reunion": fila.id_reunion, "fecha_decision": fila.fecha_decision,
            "periodo": fila.periodo, "n_train": len(train), "real": fila.decision, **pred,
            **{f"prob_tpm_dolar_{clase}": probabilidades[clase] for clase in CLASES},
        })
    return pd.DataFrame(resultados)


def metricas(predicciones, modelos):
    """Métricas multiclase con etiquetas fijas y soporte para cada clase."""
    from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, recall_score

    resultados = []
    matrices = {}
    y = predicciones.real
    for nombre in modelos:
        p = predicciones[nombre]
        sensibles = recall_score(y, p, labels=CLASES, average=None, zero_division=0)
        matrices[nombre] = confusion_matrix(y, p, labels=CLASES)
        resultados.append({
            "modelo": nombre, "n": len(y), "exactitud": accuracy_score(y, p),
            "f1_macro": f1_score(y, p, labels=CLASES, average="macro", zero_division=0),
            "exactitud_balanceada": float(np.mean(sensibles)) if y.nunique() == len(CLASES) else np.nan,
            **{f"n_{c}": int(y.eq(c).sum()) for c in CLASES},
            **{f"sens_{c}": r if y.eq(c).any() else np.nan for c, r in zip(CLASES, sensibles)},
        })
    return pd.DataFrame(resultados), matrices


def sensibilidad_eee(panel, predicciones):
    """Compara reglas de consenso con supuestos distintos sobre publicación."""
    datos = predicciones[["id_reunion", "real"]].merge(
        panel[["id_reunion", "tpm_previa_pct", "eee_previa", "eee_regla_13", "eee_mismo_mes"]],
        on="id_reunion", validate="one_to_one"
    )
    nombres = {"eee_previa": "EEE mes previo", "eee_regla_13": "EEE supuesto día 13",
               "eee_mismo_mes": "EEE mismo mes, puede usar futuro"}
    datos = datos.dropna(subset=list(nombres)).copy()
    if datos.empty:
        raise ValueError("Sin casos de EEE comunes para comparar")
    for col, nombre in nombres.items():
        signo = np.sign(datos[col].sub(datos.tpm_previa_pct).round(8)).astype(int)
        datos[nombre] = signo.map({-1: "baja", 0: "mantiene", 1: "sube"})
    return metricas(datos, list(nombres.values()))[0]
