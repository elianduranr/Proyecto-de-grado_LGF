from pathlib import Path
import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Notebooks" / "03_benchmark_estimado_ingeniero_minicarnation_light_pink.ipynb"


def md(text):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text):
    return nbf.v4.new_code_cell(text.strip())


cells = [
    md(r"""
# 03 · Benchmark del estimado del ingeniero
## MINICARNATION · LIGHT PINK

Este notebook responde una pregunta concreta: **¿qué tan cerca estuvo el estimado enviado por el ingeniero de la producción real de la semana siguiente?**

La lectura comienza con el total de cada año y luego baja a cada semana ISO. El énfasis está en el tamaño y la dirección de las equivocaciones, no en acumular métricas ni código.
"""),
    md(r"""
## Regla operativa del benchmark

- El archivo se envía el **jueves de la semana de emisión**.
- Aunque contiene un estimado de esa misma semana, ya han transcurrido cuatro días; por eso esa observación **no es un pronóstico completamente previo**.
- El benchmark principal toma la **semana siguiente al envío**: en la nomenclatura del proyecto es `horizonte = 2` y `semanas_adelante = 1`.
- Se usa la versión **original**. Los archivos cuyo nombre contiene `ajust`, `corre` o `correc` se excluyen de la evaluación y se auditan aparte.
- Se agregan todas las variedades de `MINICARNATION / LIGHT PINK` para evaluar el producto-color como una sola unidad operativa.

Convención del error:

`error_tallos = estimado - real`

- positivo: **sobreestimó**;
- negativo: **subestimó**.
"""),
    code(r"""
from pathlib import Path
import unicodedata
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Markdown

warnings.filterwarnings("ignore", category=FutureWarning)
pd.set_option("display.max_columns", 30)
pd.set_option("display.float_format", lambda x: f"{x:,.1f}")
sns.set_theme(style="whitegrid", context="notebook")

def encontrar_raiz(inicio=None):
    # Permite ejecutar el notebook desde la raíz o desde Notebooks/.
    actual = Path.cwd() if inicio is None else Path(inicio)
    for candidato in [actual, *actual.parents]:
        if (candidato / "Datos").exists() and (candidato / "Notebooks").exists():
            return candidato
    raise FileNotFoundError("No se encontró la raíz del proyecto (carpetas Datos y Notebooks).")

def clave(valor):
    texto = "" if pd.isna(valor) else str(valor)
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(texto.upper().strip().split())

RAIZ = encontrar_raiz()
DIR_EST = RAIZ / "Datos" / "Estimados semanales" / "datos preprocesados" / "archivos"
ARCH_REAL = RAIZ / "Datos" / "Producción real" / "datos preprocesados" / "produccion_semanal_gaitana.csv"
print(f"Raíz: {RAIZ}")
"""),
    md(r"""
## 1. Construir una comparación honesta

Primero se comprueba qué archivos y semanas realmente pueden compararse. No se rellenan faltantes con cero: una semana solo entra al error cuando existen tanto el estimado como la producción real.
"""),
    code(r"""
columnas = [
    "archivo_origen", "anio_carpeta", "semana_inicio_archivo", "finca",
    "producto", "color", "tipo", "anio_objetivo", "semana_objetivo",
    "horizonte", "tallos"
]

partes = []
for archivo in sorted(DIR_EST.glob("*.csv")):
    try:
        parte = pd.read_csv(archivo, usecols=columnas, low_memory=False)
        parte["archivo_csv"] = archivo.name
        partes.append(parte)
    except (ValueError, UnicodeDecodeError):
        continue

estimados = pd.concat(partes, ignore_index=True)
for col in ["finca", "producto", "color", "tipo"]:
    estimados[f"k_{col}"] = estimados[col].map(clave)
for col in ["anio_carpeta", "semana_inicio_archivo", "anio_objetivo", "semana_objetivo", "horizonte", "tallos"]:
    estimados[col] = pd.to_numeric(estimados[col], errors="coerce")

estimados["es_corregido"] = estimados["archivo_origen"].str.contains(
    r"ajust|corre", case=False, na=False, regex=True
)
filtro_producto = (
    estimados["k_finca"].eq("GAITANA")
    & estimados["k_tipo"].eq("ESTIMADO")
    & estimados["k_producto"].eq("MINICARNATION")
    & estimados["k_color"].eq("LIGHT PINK")
    & estimados["horizonte"].eq(2)  # semana siguiente al envío
)
candidatos = estimados.loc[filtro_producto].copy()

# Un total producto-color por archivo y semana; luego se elige una versión original.
por_archivo = candidatos.groupby(
    ["anio_carpeta", "semana_inicio_archivo", "anio_objetivo", "semana_objetivo",
     "archivo_origen", "archivo_csv", "es_corregido"], as_index=False
).agg(tallos_estimados=("tallos", "sum"))

originales = por_archivo.loc[~por_archivo["es_corregido"]].copy()
llave_emision = ["anio_carpeta", "semana_inicio_archivo", "anio_objetivo", "semana_objetivo"]
auditoria_originales = originales.groupby(llave_emision, as_index=False).agg(
    archivos_originales=("archivo_origen", "nunique"),
    valores_originales=("tallos_estimados", "nunique"),
    minimo_estimado=("tallos_estimados", "min"),
    maximo_estimado=("tallos_estimados", "max")
)
auditoria_originales["diferencia_entre_originales"] = (
    auditoria_originales["maximo_estimado"] - auditoria_originales["minimo_estimado"]
)

# Si hay copias originales para una emisión, la elección es determinista y queda auditada.
seleccion = (originales.sort_values(llave_emision + ["archivo_origen", "archivo_csv"])
             .drop_duplicates(llave_emision, keep="first"))

real = pd.read_csv(ARCH_REAL)
real_producto = (real.loc[
    real["k_producto"].map(clave).eq("MINICARNATION")
    & real["k_color"].map(clave).eq("LIGHT PINK")
].groupby(["anio", "semana"], as_index=False)
  .agg(tallos_reales=("tallos_reales", "sum")))

comparacion = seleccion.merge(
    real_producto,
    left_on=["anio_objetivo", "semana_objetivo"],
    right_on=["anio", "semana"],
    how="left",
    validate="many_to_one"
)
comparacion["comparable"] = comparacion["tallos_reales"].notna()
comparacion["error_tallos"] = comparacion["tallos_estimados"] - comparacion["tallos_reales"]
comparacion["error_abs_tallos"] = comparacion["error_tallos"].abs()
comparacion["error_pct"] = 100 * comparacion["error_tallos"] / comparacion["tallos_reales"].replace(0, np.nan)
comparacion["direccion"] = np.select(
    [comparacion["error_tallos"] > 0, comparacion["error_tallos"] < 0],
    ["Sobreestimó", "Subestimó"], default="Exacto"
)
comparacion["semana_iso"] = (
    comparacion["anio_objetivo"].astype("Int64").astype(str)
    + "-S" + comparacion["semana_objetivo"].astype("Int64").astype(str).str.zfill(2)
)
"""),
    code(r"""
corregidos = por_archivo.loc[por_archivo["es_corregido"]]
ambiguos = auditoria_originales.query("valores_originales > 1")
cobertura = comparacion.groupby("anio_objetivo", as_index=False).agg(
    semanas_estimadas=("semana_objetivo", "nunique"),
    semanas_comparables=("comparable", "sum"),
    primera_semana=("semana_objetivo", "min"),
    ultima_semana=("semana_objetivo", "max")
)

display(Markdown(
    f"**Control de versiones.** Se encontraron **{len(corregidos)}** combinaciones archivo-semana "
    f"marcadas como ajustadas/corregidas y se excluyeron. Hay **{len(ambiguos)}** emisiones "
    "con más de un valor original distinto; se muestran abajo para no esconder la ambigüedad."
))
display(cobertura)
if len(ambiguos):
    display(ambiguos)
else:
    print("No hay emisiones con originales numéricamente contradictorios para este producto-color y horizonte.")
"""),
    md(r"""
### Lectura de cobertura

Los años no se fuerzan a tener el mismo rango. Cada uno se interpreta con sus propias semanas disponibles, como una revisión independiente. Por eso un total anual parcial —especialmente 2026— no debe leerse como si representara 52 semanas.
"""),
    md(r"""
## 2. Resultado total por año

Esta es la vista ejecutiva. `Diferencia total` conserva el signo y revela el sesgo acumulado; `Error absoluto total` evita que una sobreestimación compense matemáticamente una subestimación.
"""),
    code(r"""
validas = comparacion.loc[comparacion["comparable"]].copy()

resumen_anual = validas.groupby("anio_objetivo", as_index=False).agg(
    semanas=("semana_objetivo", "nunique"),
    produccion_real=("tallos_reales", "sum"),
    estimado_ingeniero=("tallos_estimados", "sum"),
    diferencia_total=("error_tallos", "sum"),
    error_absoluto_total=("error_abs_tallos", "sum"),
    semanas_sobreestimadas=("direccion", lambda s: (s == "Sobreestimó").sum()),
    semanas_subestimadas=("direccion", lambda s: (s == "Subestimó").sum()),
)
resumen_anual["sesgo_pct"] = 100 * resumen_anual["diferencia_total"] / resumen_anual["produccion_real"]
resumen_anual["WAPE_pct"] = 100 * resumen_anual["error_absoluto_total"] / resumen_anual["produccion_real"]
resumen_anual["direccion_neta"] = np.select(
    [resumen_anual["diferencia_total"] > 0, resumen_anual["diferencia_total"] < 0],
    ["Sobreestimación neta", "Subestimación neta"], default="Sin sesgo neto"
)

columnas_resumen = [
    "anio_objetivo", "semanas", "produccion_real", "estimado_ingeniero",
    "diferencia_total", "sesgo_pct", "error_absoluto_total", "WAPE_pct",
    "semanas_sobreestimadas", "semanas_subestimadas", "direccion_neta"
]
display(resumen_anual[columnas_resumen].style.format({
    "produccion_real": "{:,.0f}", "estimado_ingeniero": "{:,.0f}",
    "diferencia_total": "{:+,.0f}", "sesgo_pct": "{:+.1f}%",
    "error_absoluto_total": "{:,.0f}", "WAPE_pct": "{:.1f}%"
}))
"""),
    code(r"""
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

volumen = resumen_anual.melt(
    id_vars="anio_objetivo",
    value_vars=["produccion_real", "estimado_ingeniero"],
    var_name="serie", value_name="tallos"
)
sns.barplot(data=volumen, x="anio_objetivo", y="tallos", hue="serie", ax=axes[0],
            palette=["#333333", "#e78ac3"])
axes[0].set(title="Volumen acumulado en las semanas comparables", xlabel="Año", ylabel="Tallos")
axes[0].legend(title="")

colores = np.where(resumen_anual["diferencia_total"] >= 0, "#1b9e77", "#d95f02")
axes[1].bar(resumen_anual["anio_objetivo"].astype(str), resumen_anual["diferencia_total"], color=colores)
axes[1].axhline(0, color="black", linewidth=1)
axes[1].set(title="Sesgo acumulado: estimado − real", xlabel="Año", ylabel="Diferencia en tallos")

plt.tight_layout()
plt.show()
"""),
    code(r"""
for fila in resumen_anual.itertuples():
    sentido = "por encima" if fila.diferencia_total > 0 else "por debajo"
    display(Markdown(
        f"- **{int(fila.anio_objetivo)}:** en {fila.semanas} semanas comparables, el estimado quedó "
        f"**{abs(fila.diferencia_total):,.0f} tallos {sentido}** del real en términos netos "
        f"(sesgo {fila.sesgo_pct:+.1f}%). Sin permitir compensaciones, se equivocó en "
        f"**{fila.error_absoluto_total:,.0f} tallos** (WAPE {fila.WAPE_pct:.1f}%)."
    ))
"""),
    md(r"""
## 3. Totalizado por semana ISO, separado por año

La línea muestra si el estimado siguió la forma general de la producción. Las barras muestran dónde y en qué dirección falló. Separar los años evita conectar artificialmente la semana 52 con la semana 1 y permite revisar cada campaña por sí sola.
"""),
    code(r"""
for anio, datos_anio in validas.groupby("anio_objetivo", sort=True):
    datos_anio = datos_anio.sort_values("semana_objetivo")
    fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=True,
                             gridspec_kw={"height_ratios": [2, 1]})

    axes[0].plot(datos_anio["semana_objetivo"], datos_anio["tallos_reales"],
                 marker="o", linewidth=2, color="#333333", label="Producción real")
    axes[0].plot(datos_anio["semana_objetivo"], datos_anio["tallos_estimados"],
                 marker="o", linewidth=2, color="#e78ac3", label="Estimado original")
    axes[0].set(title=f"{int(anio)} · Real frente al estimado enviado la semana anterior",
                ylabel="Tallos")
    axes[0].legend()

colores = np.where(datos_anio["error_tallos"] >= 0, "#1b9e77", "#d95f02")
    axes[1].bar(datos_anio["semana_objetivo"], datos_anio["error_tallos"], color=colores)
    axes[1].axhline(0, color="black", linewidth=1)
    axes[1].set(xlabel="Semana ISO objetivo", ylabel="Estimado − real",
                title="Verde: sobreestimó · Naranja: subestimó")
    plt.tight_layout()
    plt.show()
"""),
    md(r"""
## 4. Tabla semanal completa

Esta tabla es el totalizado solicitado. Permite rastrear cada cifra hasta el archivo original escogido y distingue magnitud (`error_abs_tallos`) de dirección (`error_tallos`).
"""),
    code(r"""
tabla_semanal = validas[[
    "semana_iso", "anio_carpeta", "semana_inicio_archivo", "archivo_origen",
    "tallos_reales", "tallos_estimados", "error_tallos", "error_abs_tallos",
    "error_pct", "direccion"
]].sort_values(["semana_iso"])

display(tabla_semanal.style.format({
    "tallos_reales": "{:,.0f}", "tallos_estimados": "{:,.0f}",
    "error_tallos": "{:+,.0f}", "error_abs_tallos": "{:,.0f}",
    "error_pct": "{:+.1f}%"
}))
"""),
    md(r"""
## 5. ¿Dónde se equivocó más?

Mirar únicamente el promedio puede ocultar semanas operacionalmente graves. Aquí se ordenan las mayores desviaciones absolutas y se resume si el error fue persistente o excepcional.
"""),
    code(r"""
peores = (validas.nlargest(12, "error_abs_tallos")[[
    "semana_iso", "tallos_reales", "tallos_estimados", "error_tallos",
    "error_pct", "direccion", "archivo_origen"
]])
display(peores.style.format({
    "tallos_reales": "{:,.0f}", "tallos_estimados": "{:,.0f}",
    "error_tallos": "{:+,.0f}", "error_pct": "{:+.1f}%"
}))

frecuencia = (validas.groupby(["anio_objetivo", "direccion"]).size()
              .unstack(fill_value=0).reset_index())
display(frecuencia)
"""),
    code(r"""
for anio, g in validas.groupby("anio_objetivo", sort=True):
    neto = g["error_tallos"].sum()
    dominante = g["direccion"].value_counts().idxmax()
    peor = g.loc[g["error_abs_tallos"].idxmax()]
    display(Markdown(
        f"### {int(anio)}\n"
        f"- La dirección más frecuente fue **{dominante.lower()}**.\n"
        f"- El sesgo neto fue **{neto:+,.0f} tallos**; este valor sí permite compensación entre semanas.\n"
        f"- La mayor equivocación ocurrió en **{peor['semana_iso']}**: "
        f"**{peor['error_tallos']:+,.0f} tallos** ({peor['direccion'].lower()})."
    ))
"""),
    md(r"""
## 6. Conclusión crítica del benchmark

Este ejercicio mide el proceso real de decisión: la versión original disponible el jueves frente a la producción de la semana siguiente. La evaluación anual debe leerse junto con cuatro ideas:

1. **Sesgo y precisión no son lo mismo.** Un sesgo neto cercano a cero puede coexistir con errores semanales grandes que se cancelan.
2. **El WAPE describe el costo agregado del error**, mientras que el signo indica si el proceso tiende a prometer más o menos tallos de los obtenidos.
3. **Cada año tiene su propia cobertura.** Los totales comparan estimado y real dentro del mismo año, pero no convierten automáticamente un año parcial en uno completo.
4. **Este es el benchmark que un modelo futuro debe superar** usando exactamente las mismas semanas objetivo, el mismo nivel producto-color y datos disponibles antes de la producción.

La siguiente ampliación natural es repetir este protocolo para todos los producto-color y luego abrir el detalle por variedad, sin cambiar la regla temporal ya fijada.
"""),
]

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3"},
}
OUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUT)
print(OUT)
