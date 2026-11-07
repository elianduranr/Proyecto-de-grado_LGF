"""Genera cuadros metodológicos limpios del recorrido semanal y diario."""
from pathlib import Path
from textwrap import fill
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = Path(__file__).parent / "Figuras_resultados"
OUT.mkdir(exist_ok=True)


def table(ax, rows, headers, widths, top, row_h, fontsize=8):
    x0 = .025
    xs = [x0]
    for width in widths:
        xs.append(xs[-1] + width)
    total = sum(widths)
    ax.add_patch(Rectangle((x0, top-row_h), total, row_h,
                           facecolor="#e5e5e5", edgecolor="none"))
    for j, header in enumerate(headers):
        ax.text(xs[j]+.008, top-row_h/2, fill(header, max(8, int(widths[j]*80)-2)), va="center", fontsize=fontsize,
                fontweight="bold", color="#111111")
    for i, row in enumerate(rows):
        ytop = top-(i+1)*row_h
        ymid = ytop-row_h/2
        if i % 2:
            ax.add_patch(Rectangle((x0, ytop-row_h), total, row_h,
                                   facecolor="#f5f5f5", edgecolor="none"))
        for j, value in enumerate(row):
            wrapped = fill(value, max(8, int(widths[j]*80)-2))
            ax.text(xs[j]+.008, ymid, wrapped, va="center", fontsize=fontsize,
                    color="#111111", wrap=True)
        ax.plot([x0, x0+total], [ytop-row_h, ytop-row_h], color="#9b9b9b", lw=.55)
    ax.plot([x0, x0+total], [top-row_h, top-row_h], color="#111111", lw=.8)


def weekly():
    fig, ax = plt.subplots(figsize=(6.1, 9.8))
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis("off")
    ax.text(.03, .97,
            "Todos estiman producción semanal para H1–H5. Sólo usan información disponible al origen.",
            fontsize=9, color="#222222")
    rows = [
        ("12 · Referencias", "Última producción real; promedio real de 4 semanas (Media4); curva sin corregir.", "Puntos de comparación", "H1–H5"),
        ("12–13 · Corrección y respaldo", "HistGradientBoosting corrige real−teoría o real−Media4. Variables: identidad, horizonte, memoria/tendencia; clima y curva para la ruta teórica.", "Usa teoría cuando aplica; Media4 como respaldo", "H1–H5"),
        ("12 · Controles", "Ridge lineal; boosting sin memoria; sin clima; y con las dos teorías previas.", "Ablaciones y alternativa lineal", "H1–H5"),
        ("14 · Señales diarias", "Añade 28 resúmenes de corte/clima pasados: ventanas 3/5/7/14 días, rezagos, dispersión, EMA y tendencias.", "Son entradas del modelo semanal", "H1–H5"),
        ("15 · Memoria y grupos", "Boosting añade memoria de hasta 12 semanas, dispersión/conteos e historia de proyecciones.", "Grupos H1–H2 y H3–H5; mezcla fijada con validación 2025", "H1–H5"),
        ("19 · Ganador anual", "Dos HistGradientBoosting sin clima: ambos corrigen teoría o Media4; uno se ajusta para H1–H2 y otro para H3–H5.", "La selección se fijó antes de evaluar 2026", "H1–H5"),
        ("21–25 · Especialistas recientes", "Modelos separados por horizonte/producto, combinados con el modelo general.", "H1 conserva H1–H2; H2 separado; H3–H5 especialistas + general", "H1–H5"),
    ]
    table(ax, rows, ["Cuadernos / modelo", "Qué aprende y qué variables recibe", "Cómo se combina", "Horizontes"],
          [.20, .38, .24, .15], .89, .105, fontsize=7.8)
    fig.savefig(OUT / "metodologia_modelo_semanal.png", dpi=220,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


def daily():
    fig, ax = plt.subplots(figsize=(6.1, 6.4))
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis("off")
    ax.text(.03, .97, "(En revisión: piloto exploratorio; no reemplaza el pronóstico semanal.)",
            fontsize=9, color="#111111")
    rows = [
        ("Referencias · 02", "Reparto uniforme; perfil de volumen/frecuencia de las 8 semanas anteriores.", "No entrenadas", "7 días de H1"),
        ("Boosting autónomo · 02/05", "HistGradientBoosting usa producción pasada, calendario y clima pasado; predice cada día sin recibir el total semanal.", "WAPE 26,72 %", "22.973 días"),
        ("Boosting reconciliado · 02/05", "Boosting estima pesos de los 7 días y distribuye el total semanal; la suma diaria conserva ese total.", "WAPE 27,26 %", "22.973 días"),
        ("SARIMA · 03/04", "(1,0,1)×(0,1,1,7), log(1+tallos), 365 días de historia; 3 series de mayor volumen.", "Serie temporal", "Piloto mensual"),
        ("SARIMAX · 03/04", "Mismo SARIMA con clima rezagado 7 días; no usa clima futuro observado.", "WAPE 24,53 %*", "Mismos días piloto"),
    ]
    table(ax, rows, ["Modelo", "Entradas y tarea", "Resultado", "Alcance"],
          [.24, .44, .16, .13], .84, .105, fontsize=8.1)
    ax.text(.035, .11,
            "* Menor WAPE del piloto pequeño; no se compara directamente con toda la finca.\n"
            "Aún no hay benchmark diario equivalente del ingeniero.",
            fontsize=8.8, va="bottom", color="#111111")
    fig.savefig(OUT / "metodologia_modelo_diario.png", dpi=220,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    weekly()
    daily()
