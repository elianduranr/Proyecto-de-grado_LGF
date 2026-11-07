"""Gráfico comparativo a color del modelo semanal seleccionado frente al ingeniero."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

OUT = Path(__file__).parent / "Figuras_resultados" / "comparacion_modelo_semanal_ganador.png"

# Métricas del panel anual estricto actualizado. Sesgo = predicción - real.
labels = ["H1", "H2", "H3", "H4", "H5", "Total"]
wape_modelo = np.array([15.53, 17.49, 20.33, 21.78, 22.20, 19.36])
wape_ingeniero = np.array([16.93, 19.16, 20.26, 20.97, 21.60, 19.71])
sesgo_modelo = np.array([-1.34, -2.01, -2.46, -3.18, -2.97, -2.36])
sesgo_ingeniero = np.array([-7.54, -7.97, -9.38, -11.52, -13.09, -9.81])

plt.rcParams.update({"font.family": "serif", "font.size": 9, "text.color": "black", "axes.labelcolor": "black", "xtick.color": "black", "ytick.color": "black"})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.1, 3.9), gridspec_kw={"width_ratios": [1, 1.08]})
y = np.arange(len(labels))
height = .34
ax1.barh(y-height/2, wape_modelo, height, color="#4472C4", label="Boosting sin clima")
ax1.barh(y+height/2, wape_ingeniero, height, color="#ED7D31", label="Ingeniero")
ax1.set_yticks(y, labels); ax1.invert_yaxis(); ax1.set_xlabel("WAPE (%)")
ax1.set_title("Error absoluto", loc="left", fontweight="bold")
ax1.grid(axis="x", color="#b7b7b7", linewidth=.5); ax1.set_axisbelow(True)
ax1.spines[["top", "right", "left"]].set_visible(False)
for vals, offs in [(wape_modelo, -height/2), (wape_ingeniero, height/2)]:
    for i, v in enumerate(vals): ax1.text(v+.12, i+offs, f"{v:.2f}", va="center", fontsize=7.5)
ax2.axvline(0, color="black", linewidth=.8)
ax2.plot(sesgo_modelo, y, "o", color="#4472C4", label="Boosting sin clima")
ax2.plot(sesgo_ingeniero, y, "s", color="#ED7D31", linestyle="none", label="Ingeniero")
for i, v in enumerate(sesgo_modelo): ax2.text(v+.18, i-.12, f"{v:.2f}", fontsize=7.2, va="center")
for i, v in enumerate(sesgo_ingeniero): ax2.text(v-.18, i+.14, f"{v:.2f}", fontsize=7.2, va="center", ha="right")
ax2.set_yticks(y, labels); ax2.invert_yaxis(); ax2.set_xlabel("Sesgo (%) · negativo = subestima")
ax2.set_title("Dirección del error", loc="left", fontweight="bold")
ax2.grid(axis="x", color="#b7b7b7", linewidth=.5); ax2.set_axisbelow(True)
ax2.spines[["top", "right", "left"]].set_visible(False)
handles, names = ax1.get_legend_handles_labels()
fig.legend(handles, names, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(.5, -.015))
fig.tight_layout(rect=(0, .06, 1, 1), w_pad=1.5)
fig.savefig(OUT, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
