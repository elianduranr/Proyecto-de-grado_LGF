from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).parent.parent
DATA = ROOT / "Datos_analiticos_proyecto/revision_clima_finca/comparacion_clima_curvas_2026.parquet"
OUT = Path(__file__).parent / "Figuras_resultados"
OUT.mkdir(exist_ok=True)
d = pd.read_parquet(DATA)
d = d.loc[d.grupo_comparacion.eq("principal_estricta_nominal")].copy()
methods = {
    "Sin clima": "Sin_clima",
    "Clima básico": "Clima_basico",
    "Clima ampliado": "Clima_ampliado",
    "Curva Gaitana + clima": "Curva_Gaitana_clima",
    "Ingeniero": "ingeniero",
}
horizons = range(1, 6)
colors = ["#276FBF", "#F28E2B", "#59A14F", "#B07AA1", "#4E4E4E"]


def score(series, column, signed=False):
    error = series[column] - series.y
    return 100 * (error.sum() if signed else error.abs().sum()) / series.y.sum()


def line_plot(filename, metric, ylabel, title, signed=False):
    fig, ax = plt.subplots(figsize=(9.5, 5.3))
    for (label, column), color in zip(methods.items(), colors):
        vals = [score(d.loc[d.horizonte.eq(h)], column, signed=signed) for h in horizons]
        ax.plot(list(horizons), vals, marker="o", linewidth=2, label=label, color=color)
    if signed:
        ax.axhline(0, color="#777", linewidth=0.8)
    ax.set_xticks(list(horizons), [f"H{h}" for h in horizons])
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Horizonte")
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / filename, dpi=200, bbox_inches="tight")
    plt.close(fig)


line_plot("clima_modelos_horizonte.png", "wape", "WAPE (%)", "Error semanal por horizonte · panel estricto actualizado")
line_plot("clima_sesgo_horizonte.png", "bias", "Sesgo (%)", "Sesgo por horizonte · estimado menos real", signed=True)

# El movimiento se muestra como el cambio de predicción al añadir clima básico.
change = d.assign(cambio=d.Clima_basico - d.Sin_clima)
fig, ax = plt.subplots(figsize=(9.5, 5.3))
parts = [change.loc[change.horizonte.eq(h), "cambio"].dropna() for h in horizons]
ax.boxplot(parts, tick_labels=[f"H{h}" for h in horizons], showfliers=False, patch_artist=True,
           boxprops={"facecolor": "#9EC9D8", "edgecolor": "#276FBF"},
           medianprops={"color": "#D1495B", "linewidth": 1.8})
ax.axhline(0, color="#777", linewidth=0.8)
ax.set_xlabel("Horizonte")
ax.set_ylabel("Cambio de estimación (tallos)")
ax.set_title("Movimiento al añadir clima básico · panel estricto actualizado")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "clima_movimiento_estimado.png", dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"Actualizadas {len(d):,} comparaciones estrictas en las tres figuras.")
