"""Gráficos del notebook y PNG para revisar, presentar o editar."""
import matplotlib.pyplot as plt
import numpy as np

from src.processing.estudio_final import CLASES, COLORES, EDA, MODELOS_PRINCIPALES, PERIODOS

AZUL = "#2364AA"
OSCURO = "#172B42"
GRIS = "#536579"


def periodos(panel):
    conteos = panel.groupby(["periodo", "decision"], observed=True).size().unstack(fill_value=0)
    conteos = conteos.reindex(index=PERIODOS, columns=CLASES, fill_value=0)
    porcentajes = conteos.div(conteos.sum(axis=1), axis=0).mul(100)
    fig, ax = plt.subplots(figsize=(9, 4.2), layout="constrained")
    base = np.zeros(len(conteos))
    for clase in CLASES:
        parte = porcentajes[clase]
        barras = ax.bar(PERIODOS, parte, bottom=base, color=COLORES[clase], label=clase.capitalize(), width=.62)
        ax.bar_label(barras, [str(n) if p >= 9 else "" for n, p in zip(conteos[clase], parte)],
                     label_type="center", color="white", fontsize=12, fontweight="bold")
        base += parte.to_numpy()
    ax.set(ylabel="% de anuncios del período", ylim=(0, 116),
           title="La composición de las decisiones cambia entre períodos")
    for i, n in enumerate(conteos.sum(axis=1)):
        ax.text(i, 104, f"n = {n}", ha="center", color=GRIS)
    ax.legend(loc="lower center", bbox_to_anchor=(.5, -0.19), ncols=3, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    return fig, conteos


def distribuciones(panel):
    fig, axes = plt.subplots(2, 3, figsize=(13.2, 6.9), layout="constrained")
    for ax, (var, (nombre, unidad)) in zip(axes.flat, EDA.items()):
        muestras = [panel.loc[panel.decision.eq(c), var].dropna() for c in CLASES]
        cajas = ax.boxplot(muestras, patch_artist=True, widths=.51,
                           medianprops={"color": OSCURO, "linewidth": 2})
        for caja, clase in zip(cajas["boxes"], CLASES):
            caja.set(facecolor=COLORES[clase], alpha=.4)
        ax.set_xticks(range(1, 4), [f"{c.capitalize()}\nn={len(s)}" for c, s in zip(CLASES, muestras)])
        ax.set(title=nombre, ylabel=unidad)
        ax.grid(axis="y", color="#e3eaf2", linewidth=.7)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Predictores por clase en las primeras 60 reuniones ordinarias", fontsize=17, color=OSCURO)
    return fig


def niveles_y_cambios(panel):
    pares = [
        ("dolar_nivel", "dolar_ret_20", "Dólar observado", ("CLP/USD", "% a 20 cotizaciones")),
        ("cobre_nivel", "cobre_ret_20", "Cobre BML", ("USD/libra", "% a 20 cotizaciones")),
        ("imacec_nivel", "imacec_12m", "IMACEC original", ("Índice", "% interanual")),
        ("desemp_nivel", "desemp_12m", "Desempleo", ("Nivel (%)", "Cambio interanual (pp)")),
        ("ipc_mensual", "ipc_12m", "IPC", ("% mensual", "% acumulado en 12 meses")),
    ]
    tablas = []
    for nivel, cambio, nombre, unidades in pares:
        # Comparar niveles y transformaciones sobre los mismos anuncios.
        comun = panel.dropna(subset=[nivel, cambio])
        for clase in CLASES:
            grupo = comun.loc[comun.decision.eq(clase)]
            tablas.append({
                "serie": nombre, "decision": clase, "n_comun": len(grupo),
                "unidad_nivel": unidades[0], "mediana_nivel": grupo[nivel].median(),
                "unidad_cambio": unidades[1], "mediana_cambio": grupo[cambio].median(),
            })
    return tablas


def f1(resultados):
    datos = resultados.set_index("modelo").loc[MODELOS_PRINCIPALES]
    fig, ax = plt.subplots(figsize=(8.5, 3.9), layout="constrained")
    barras = ax.barh(datos.index, datos.f1_macro, color=["#9aaab9", "#536579", "#89afd3", AZUL], height=.57)
    ax.bar_label(barras, [f"{v:.3f}".replace(".", ",") for v in datos.f1_macro], padding=7, fontsize=12)
    ax.invert_yaxis()
    ax.set(xlim=(0, 1), xlabel="F1 macro (0 a 1)", title="Evaluación cronológica en las mismas reuniones")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color="#e3eaf2")
    ax.set_axisbelow(True)
    return fig


def confusiones(matrices):
    nombres = ["Persistencia", "Logística TPM + dólar"]
    nmax = max(matrices[nombre].max() for nombre in nombres)
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.2), layout="constrained")
    for ax, nombre in zip(axes, nombres):
        matriz = matrices[nombre]
        ax.imshow(matriz, cmap="Blues", vmin=0, vmax=nmax)
        for i, j in np.ndindex(matriz.shape):
            ax.text(j, i, matriz[i, j], ha="center", va="center", fontsize=15,
                    color="white" if matriz[i, j] > nmax * .55 else OSCURO)
        etiquetas = [c.capitalize() for c in CLASES]
        ax.set_xticks(range(3), etiquetas)
        ax.set_yticks(range(3), etiquetas)
        ax.set(title=nombre, xlabel="Pronóstico", ylabel="Decisión real")
    return fig
