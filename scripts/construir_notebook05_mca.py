"""Construye el notebook 05 con carga histórica, MCA, análisis semanal y comentarios calculados."""
from pathlib import Path
import shutil
import tempfile
from datetime import datetime
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Notebooks/05_MCA_2026.ipynb'
cells=[]
def md(s): cells.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): cells.append(nbf.v4.new_code_cell(s.strip()))

md('''# 05 · MCA de la producción histórica de GAITANA

## Perfil productivo, grado comercial y recurrencia semanal

Este cuaderno analiza **toda la producción disponible de GAITANA**, leyendo los Excel de `Datos/Producción real`. El nombre del notebook se conserva; el periodo por defecto incluye todos los años encontrados. El año y la semana se calculan con calendario ISO desde la fecha de corte.

Preguntas:
1. ¿Qué categorías de producto y color suelen aparecer asociadas?
2. ¿Cómo se relaciona el grado comercial con ese perfil, sin confundir clasificación con calidad?
3. ¿Las mismas semanas muestran composiciones productivas parecidas entre años?
4. ¿Cambian las conclusiones al modificar las variables activas o la ponderación?

La limpieza sigue la lógica del notebook **03, sección “Importación de producción real y su respectiva limpieza”**. Se elimina `Sector`: identifica al supervisor y no forma parte de este estudio. Las conclusiones se generan con las salidas de esta ejecución. Es un análisis descriptivo de asociaciones, no un modelo causal ni un pronóstico.
''')
md('''## 0. Configuración y procedencia

Se reconocen las hojas por sus columnas de producción, no por un nombre fijo como `BD`. Esto incluye las continuaciones de fin de año. Se excluyen hojas auxiliares de supervisores y tablas sin ese esquema. Se filtra **GAITANA antes de imputar**, para que otra finca no aporte referencias al corte.

`ANIOS_ARCHIVO = None` carga todos los libros; por ejemplo `[2026]` limita la selección a ese archivo. `ANIOS_ISO` permite filtrar los registros por año ISO después de consolidar. La caché se guarda dentro de `Datos/modelado/mca_produccion` y se invalida cuando cambian las fuentes o las reglas.
''')
code('''from pathlib import Path
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Markdown, FileLink

RAIZ = next(p for p in [Path.cwd().resolve(), *Path.cwd().resolve().parents]
            if (p / "Notebooks").is_dir() and (p / "Datos").is_dir())
if str(RAIZ / "scripts") not in sys.path:
    sys.path.insert(0, str(RAIZ / "scripts"))
import mca_produccion as mp
import mca_auditoria as ma

CARPETA_PRODUCCION = RAIZ / "Datos" / "Producción real"
CARPETA_CACHE = RAIZ / "Datos" / "modelado" / "mca_produccion"
SALIDA = RAIZ / "Notebooks" / "informes" / "mca_gaitana"
SALIDA.mkdir(parents=True, exist_ok=True)
ANIOS_ARCHIVO = None
ANIOS_ISO = None
UMBRAL_RARO = 0.001  # Menos del 0,1 % de tallos: OTROS solo en variables del MCA.
SEMILLA = 42

pd.set_option("display.max_columns", 30)
pd.set_option("display.float_format", lambda x: f"{x:,.3f}")
sns.set_theme(style="whitegrid", palette="colorblind")
TABLAS = {}
COMENTARIOS = []

def comentar(texto):
    COMENTARIOS.append(texto)
    display(Markdown(texto))

def mostrar(nombre, tabla, n=20):
    TABLAS[nombre] = tabla.copy()
    display(tabla.head(n))

def guardar_figura(nombre):
    plt.tight_layout()
    plt.savefig(SALIDA / (nombre + ".png"), dpi=160, bbox_inches="tight")
    plt.show()
    plt.close()

print("Carpeta fuente:", CARPETA_PRODUCCION)
print("Finca del análisis: GAITANA")
display(pd.DataFrame([{"archivo": p.name, "MiB": p.stat().st_size / 1024**2}
                     for p in sorted(CARPETA_PRODUCCION.glob("*.xlsx")) if not p.name.startswith("~$")]))
''')
code('''# La primera ejecución lee Excel; las siguientes reutilizan las cachés verificadas.
prod, auditoria_fuentes, control_limpieza, solapamientos = mp.obtener_base(
    CARPETA_PRODUCCION, CARPETA_CACHE, ANIOS_ARCHIVO
)
if ANIOS_ISO is not None:
    prod = prod.loc[prod["anio"].isin(ANIOS_ISO)].copy()
assert prod["finca"].eq("GAITANA").all()

mostrar("fuentes", auditoria_fuentes.drop(columns="fincas", errors="ignore"), n=40)
mostrar("limpieza", control_limpieza, n=30)
print("Filas limpias seleccionadas:", f"{len(prod):,}")
print("Rango de fechas:", prod.fecha_corte.min(), "→", prod.fecha_corte.max())
''')
md('''### 0.1. Qué se elimina, qué se imputa y qué se conserva

- Se retiran filas sin datos de producción y registros de otras fincas; ambos conteos quedan en la auditoría.
- Se eliminan del análisis `Sector` (supervisor), `Inventario Físico`, `Reintegro`, `Ajuste`, `Fecha Descarga` y columnas sin encabezado útil. El supervisor tampoco interviene en la imputación, conciliación de copias ni preparación de categorías.
- Se mantienen archivo, hoja y fila de origen, así como las cantidades, año, semana, hora y tipo de corte originales.
- Las copias idénticas **entre fuentes** se concilian sin eliminar repeticiones dentro de una misma hoja: para cada registro idéntico se conserva la mayor multiplicidad observada en una fuente. Esto supone que una coincidencia completa entre fuentes es una copia; el detalle retirado queda disponible para revisión.
- `Tipo Corte` se imputa con la moda de **producto + color + variedad** en la semana anterior, actual y siguiente. En empate se usa el orden de la etiqueta normalizada. No se imputa recursivamente ni se toma una moda global para años sin referencia.
- Si no hay referencia, el corte permanece faltante. No se inventan grados, fechas ni cantidades. Las filas con tallos no positivos o fecha inválida quedan en la base limpia y se separan del MCA, que requiere pesos positivos.

La hora se normaliza sin asignar una fecha ficticia. `Lote` se conserva para trazabilidad, pero no participa como categoría del MCA.
''')
code('''calidad_anual = prod.groupby("anio", dropna=False).agg(
    registros=("tallos", "size"), tallos=("tallos", "sum"),
    semanas=("semana", "nunique"), primera_fecha=("fecha_corte", "min"),
    ultima_fecha=("fecha_corte", "max"), cortes_imputados=("corte_imputado", "sum"),
    cortes_faltantes=("tipo_corte", lambda s: s.isna().sum()),
    grados_faltantes=("grado", lambda s: s.isna().sum()),
    pesos_no_validos=("peso_valido", lambda s: (~s).sum())
).reset_index()
calidad_anual["grado_faltante_pct"] = 100 * calidad_anual.grados_faltantes / calidad_anual.registros
calidad_anual["corte_faltante_pct"] = 100 * calidad_anual.cortes_faltantes / calidad_anual.registros
mostrar("calidad_anual", calidad_anual)

anios_sin_corte = calidad_anual.loc[calidad_anual.corte_faltante_pct > 50, "anio"].dropna().astype(int).tolist()
comentar(
    f"**Lectura de la limpieza.** Se conservan **{len(prod):,} registros** y "
    f"**{prod.tallos.sum():,.0f} tallos** en la selección. Hay **{len(solapamientos):,} copias entre fuentes** "
    f"retiradas antes del filtro de año ISO. Se imputaron **{prod.corte_imputado.sum():,} cortes**; "
    f"**{prod.tipo_corte.isna().sum():,}** siguen sin referencia. "
    f"Los años con más de la mitad de sus registros sin corte son **{anios_sin_corte or 'ninguno'}**. "
    "En la siguiente sección se ensaya una imputación adicional con validación entre años. "
    "Los faltantes de grado se revisan por año antes de interpretar cambios comerciales."
)
''')
md('''### 0.2. Imputación adicional sin perder registros

Se mantienen `grado`, `tipo_corte` y `tipo_corte_original`. Se añaden `grado_analisis` y `tipo_corte_analisis`, indicadores de imputación, método, número de donantes y acuerdo mínimo. **No se modifican tallos ni fechas ni se elimina ninguna fila por faltantes.**

La referencia es la misma combinación **producto + color + variedad**, solo de GAITANA. Se exige que la categoría dominante sea la misma en todos sus años con datos, al menos dos años, al menos 30 registros por año y un acuerdo mínimo del 95 % en cada año. Los valores ya imputados nunca actúan como donantes.

Se prueba la regla ocultando un año completo cada vez. Se descarta el traslado histórico de una variable si algún año con al menos 1.000 predicciones tiene menos del 90 % de acierto por registros o por tallos. Son umbrales exploratorios explícitos, no garantías estadísticas. El acuerdo de donantes **no es una probabilidad calibrada**, y la validación con datos observados no demuestra acierto en años donde falta toda la columna.

Cuando no hay evidencia suficiente se usa **`SIN_REFERENCIA`**, conservando la fila. Esa etiqueta permite incluir todos los registros en el MCA de sensibilidad; no equivale a conocer su grado o corte. No se imputan identificadores de lote, horas ni cantidades por una moda global.
''')
code('''n_antes, tallos_antes = len(prod), prod.tallos.sum()
imputacion_anual, validacion_imputacion, referencias_imputacion = ma.imputar_sin_perder(prod)
assert len(prod) == n_antes and np.isclose(prod.tallos.sum(), tallos_antes)
mostrar("imputacion_anual", imputacion_anual, n=40)
mostrar("validacion_imputacion", validacion_imputacion, n=20)
mostrar("referencias_imputacion", referencias_imputacion, n=15)
for variable in ["grado", "tipo_corte"]:
    val=validacion_imputacion.loc[validacion_imputacion.variable.eq(variable)]
    nuevos=prod[variable+"_metodo"].eq("referencia_estable_entre_anios").sum()
    pendientes=prod[variable+"_metodo"].eq("sin_referencia").sum()
    habilitada=bool(val.regla_habilitada.any())
    comentar(
        f"**Imputación de {variable}.** Se completan **{nuevos:,} registros adicionales**; "
        f"**{pendientes:,}** se conservan como SIN_REFERENCIA en la columna analítica. "
        f"La regla entre años queda **{'habilitada' if habilitada else 'descartada por su validación'}**. "
        f"El acierto por registros en años evaluables va de **{val.acierto_pct.min():.1f} %** "
        f"a **{val.acierto_pct.max():.1f} %**, con coberturas entre "
        f"**{val.cobertura_pct.min():.1f} % y {val.cobertura_pct.max():.1f} %**. "
        "La escasa cobertura limita el alcance del acierto. No se conoce el valor real de los faltantes históricos."
    )
''')
md('''## 1. Cobertura temporal y composición de la producción

Una semana ausente no se reemplaza automáticamente por producción cero. Las comparaciones entre años usan las semanas efectivamente disponibles. La última semana de cada archivo puede estar incompleta, y un día sin registro no necesariamente significa un error: podría ser festivo o no haber cosecha.
''')
code('''cobertura = prod.loc[prod.fecha_corte.notna()].groupby(["anio", "semana"]).agg(
    tallos=("tallos", "sum"), registros=("tallos", "size"),
    dias_con_registro=("fecha_corte", lambda s: s.dt.normalize().nunique())
).reset_index()
mostrar("cobertura_semanal", cobertura, n=12)
plt.figure(figsize=(15, 4))
matriz_dias = cobertura.pivot(index="anio", columns="semana", values="dias_con_registro")
sns.heatmap(matriz_dias, cmap="YlGnBu", vmin=0, vmax=7,
            cbar_kws={"label": "Días con registro; blanco = semana ausente"})
plt.title("GAITANA · Cobertura observada por año y semana ISO")
guardar_figura("01_cobertura_semanal")

base_mca, diccionario_categorias = mp.preparar_categorias(prod, UMBRAL_RARO)
mostrar("categorias", diccionario_categorias.sort_values(["variable", "tallos"], ascending=[True, False]), n=18)
mix_producto = base_mca.groupby("K_producto", observed=True).tallos.agg(["sum", "size"])
mix_producto.columns = ["tallos", "registros"]
mix_producto["porcentaje"] = 100 * mix_producto.tallos / mix_producto.tallos.sum()
mix_producto = mix_producto.sort_values("tallos", ascending=False)
mostrar("mix_producto", mix_producto.reset_index())

comentar(
    f"**Cobertura del análisis.** El MCA utiliza **{len(base_mca):,} filas con fecha válida y tallos positivos**, "
    f"equivalentes a **{base_mca.tallos.sum():,.0f} tallos**, en **{base_mca.anio.nunique()} años ISO**. "
    f"El producto con mayor masa es **{mix_producto.index[0]}**, con **{mix_producto.porcentaje.iloc[0]:.1f} %**. "
    "Las categorías con mayor volumen pesan más en el análisis ponderado; esto es intencional porque "
    "la unidad de interés es el tallo. Los totales de años parciales no son comparables directamente con años completos."
)
''')
md('''### 1.1. Auditoría del valor atípico de 2021

Se señala el máximo semanal de 2021 y se muestra el umbral exploratorio `Q3 + 1,5 × IQR` de sus totales semanales. Superar ese umbral no demuestra un error: puede existir estacionalidad.

Se rastrea el pico hasta archivo, hoja y fila del Excel. Los bloques son tramos consecutivos de filas de la misma fuente. Se comparan conservando la multiplicidad por **fecha, producto, color, variedad, invernadero y tallos**, sin usar el supervisor. La coincidencia es una señal de revisión, no una prueba de que dos cosechas sean la misma. Se conservan todas las filas y se muestran escenarios alternativos por separado.
''')
code('''auditoria_2021=ma.auditar_pico_2021(prod)
mostrar("alertas_semanales_2021", auditoria_2021["semanas"], n=60)
if "detalle" in auditoria_2021:
    for clave in ["bloques", "coincidencias", "escenarios", "productos", "dias"]:
        mostrar("pico2021_"+clave, auditoria_2021[clave], n=30)
    detalle_2021=auditoria_2021["detalle"]
    muestras_originales=ma.muestras_fuente(auditoria_2021["bloques"],CARPETA_PRODUCCION,CARPETA_CACHE)
    mostrar("pico2021_muestra_excel", muestras_originales)
    detalle_2021.to_parquet(CARPETA_CACHE/"detalle_pico_2021.parquet", index=False)
    # Exportar las filas completas al Excel, sin truncarlas al número que se muestra.
    mostrar("pico2021_filas", detalle_2021, n=8)
    week=auditoria_2021["semana"]
    pares=auditoria_2021["coincidencias"]
    comentar(
        f"**Pico de 2021: semana {week}**, del {detalle_2021.fecha_corte.min().date()} "
        f"al {detalle_2021.fecha_corte.max().date()}, con **{detalle_2021.tallos.sum():,.0f} tallos** "
        f"y **{len(detalle_2021):,} registros**. Los bloques y sus filas de origen se detallan arriba. "
        "Las hipótesis de copia no modifican el total observado ni el análisis principal."
    )
    if not pares.empty:
        par=pares.loc[pares.porcentaje_bloque_menor.idxmax()]
        comentar(
            f"**Posible duplicación.** Entre los bloques {int(par.bloque_a)} y {int(par.bloque_b)} "
            f"coinciden **{int(par.registros_coincidentes):,} registros** "
            f"(**{par.porcentaje_bloque_menor:.2f} %** del bloque menor), respetando multiplicidades. "
            "La evidencia apunta a tres posibilidades: (1) una copia accidental dentro de la misma hoja, "
            "(2) una segunda exportación o fotografía operativa de la misma cosecha, enriquecida con "
            "identificadores de inventario, o (3) una segunda versión con correcciones. "
            "No parece una segunda cosecha independiente porque fecha, producto, color, variedad e "
            "invernadero se repiten fila a fila. En las 43 filas restantes, el primer bloque suma "
            "4.177 tallos y el segundo 3.440: hay una diferencia neta de 737 tallos, siempre con "
            "80 tallos en el segundo bloque. Esto prueba que existe una actualización o diferencia de "
            "carga, pero no permite decidir cuál cantidad es correcta. El segundo bloque además tiene "
            "Estado Inventario informado en las 16.168 filas, mientras el primero no lo tiene. "
            "Debe revisarse la procedencia y fecha de exportación antes de eliminar o reemplazar un bloque."
        )
    fig,ax=plt.subplots(figsize=(12,4))
    weekly=auditoria_2021["semanas"]
    ax.plot(weekly.semana,weekly.tallos/1e6,label="Observado completo")
    for i,row in auditoria_2021["escenarios"].iloc[1:].iterrows():
        ax.scatter([week],[row.tallos/1e6],marker="x",s=100,label=row.escenario)
    ax.set(title="Pico 2021: observado y escenarios de revisión",xlabel="Semana ISO",ylabel="Millones de tallos")
    ax.legend(fontsize=8); guardar_figura("01b_auditoria_pico_2021")
    # Regla de decisión explícita: separar alerta estadística de decisión de depuración.
    vecinos=auditoria_2021["semanas"].loc[auditoria_2021["semanas"].semana.between(40,44)].copy()
    mediana_vecinos=vecinos.loc[vecinos.semana.ne(week),"tallos"].median()
    ratio=float(vecinos.loc[vecinos.semana.eq(week),"tallos"].iloc[0]/mediana_vecinos)
    alerta_iqr=bool(vecinos.loc[vecinos.semana.eq(week),"alerta_IQR"].iloc[0])
    decision=("REVISAR EN ORIGEN antes de usar la semana 42 para decisiones o modelos"
              if alerta_iqr and ratio>=1.5 else
              "conservar como observada y monitorear")
    mostrar("decision_pico_2021",pd.DataFrame([{
        "semana":week,"tallos_semana":float(vecinos.loc[vecinos.semana.eq(week),"tallos"].iloc[0]),
        "mediana_semanas_vecinas_40_44":float(mediana_vecinos),
        "multiplo_mediana_vecinas":ratio,"supera_IQR":alerta_iqr,
        "decision":decision,
        "accion":("confirmar si ambos bloques corresponden a cosechas distintas; si no, corregir la fuente y regenerar resultados"
                   if "REVISAR" in decision else "mantener y documentar")
    }]))
    comentar(
        f"**Decisión sobre la semana irregular.** La semana {week} tiene **{ratio:.2f} veces** "
        f"la mediana de sus semanas vecinas (40–44) y **{'supera' if alerta_iqr else 'no supera'}** el umbral IQR. "
        f"Por eso la decisión operativa es: **{decision}**. "
        "La alerta no autoriza borrar la semana ni convertirla en cero. Primero se debe confirmar en el Excel "
        "si los dos bloques son versiones de la misma carga. Hasta esa confirmación, los análisis descriptivos "
        "reportan el dato observado y separan este caso como alerta de calidad."
    )
# Base enriquecida: originales, imputaciones y alertas. Todas las filas limpias permanecen.
prod.to_parquet(CARPETA_CACHE/"produccion_gaitana_auditada.parquet", index=False)
''')
md('''## 2. Variables y diagnóstico antes del mapa

**Análisis principal:** producto y color activos. Con dos variables, este ajuste es el caso bivariado del MCA, estrechamente relacionado con el AC de la tabla producto–color; sirve como referencia del catálogo, no como una explicación multivariable completa. Describe toda la producción con fecha válida y peso positivo. No usa grado o corte para construir sus ejes, porque sus faltantes cambian entre años. Los ajustes con grado o semana incorporan tres variables activas.

**Suplementarias:** semana ISO, año ISO, grado comercial, corte, invernadero y variedad. Su proyección permite interpretar el mapa sin obligarlo a separar esas categorías. Los faltantes se identifican como `SIN_DATO`, no como una categoría agronómica real.

**Segundo MCA:** incorpora grado como activo exclusivamente donde está registrado. Se comparará su cobertura y sensibilidad. **Semana activa** se probará aparte: su orden no interviene en el MCA estándar y 52–53 niveles pueden ocupar muchos ejes.

No se incluyen variedad y producto simultáneamente como activos por defecto: el catálogo puede hacerlos casi deterministas. La V de Cramér se usa aquí como magnitud descriptiva, ponderada por tallos; no se calculan p-valores suponiendo millones de tallos independientes.
''')
code('''ACTIVAS = ["K_producto", "K_color"]
SUPLEMENTARIAS = ["K_semana", "K_anio", "K_grado", "K_tipo_corte", "K_invernadero", "K_variedad"]
variables_diag = ACTIVAS + ["K_grado", "K_tipo_corte", "K_semana", "K_anio"]
diag = pd.DataFrame(index=variables_diag, columns=variables_diag, dtype=float)
for i, a in enumerate(variables_diag):
    for b in variables_diag[i+1:]:
        diag.loc[a,b] = diag.loc[b,a] = mp.cramer(mp.tabla_pesos(base_mca,a,b))
mostrar("asociaciones", diag.reset_index(names="variable"))
plt.figure(figsize=(10, 7))
sns.heatmap(diag, annot=True, fmt=".3f", vmin=0, vmax=1, cmap="YlGnBu")
plt.title("V de Cramér descriptiva · ponderada por tallos")
guardar_figura("02_asociaciones")

pares = [(a,b,diag.loc[a,b]) for i,a in enumerate(variables_diag) for b in variables_diag[i+1:]
         if pd.notna(diag.loc[a,b])]
mayor = max(pares, key=lambda x: x[2])
comentar(
    f"**Diagnóstico.** La asociación más alta de esta matriz es **{mayor[0]}–{mayor[1]}**, "
    f"con **V = {mayor[2]:.3f}**. Entre producto y color es **{diag.loc['K_producto','K_color']:.3f}**; "
    f"entre semana y producto, **{diag.loc['K_semana','K_producto']:.3f}**. "
    "V describe una relación global, no su causa ni su estabilidad anual. Las asociaciones con SIN_DATO "
    "pueden reflejar cambios de registro. Para semana, agrupar todos los años puede diluir patrones "
    "distintos o confundirlos con diferencias de cobertura: se revisará su recurrencia explícitamente."
)
''')
md('''## 3. MCA principal: ajuste y validaciones

La indicadora contiene una columna por categoría activa. Cada registro contribuye en proporción a sus tallos. Se agrupan perfiles idénticos y se descompone la matriz de productos `SᵀS` de los residuos estandarizados; así no es necesario expandir millones de tallos ni conservar una indicadora densa de todas las filas.

Se comprueba la inercia total `(J − Q) / Q`, la suma de contribuciones por eje y el centrado de coordenadas. Se muestran inercia cruda y correcciones de Benzécri y Greenacre. Las coordenadas del mapa corresponden al MCA original; la corrección solo cambia cómo se comunica la inercia. Las fórmulas y el código numérico están en `scripts/mca_produccion.py`.
''')
code('''mca = mp.ajustar_mca(base_mca, ACTIVAS)
categorias = mp.resultados_categorias(mca)
n = mca["n_dim"]
inercia = pd.DataFrame({
    "dimension": [f"Dim{k+1}" for k in range(n)], "autovalor": mca["eig"][:n],
    "cruda_pct": mca["inercia_cruda_pct"][:n],
    "benzecri_pct": mca["inercia_benzecri_pct"][:n],
    "greenacre_pct": mca["inercia_greenacre_pct"][:n]
})
inercia["greenacre_acumulada_pct"] = inercia.greenacre_pct.cumsum()
mostrar("inercia_principal", inercia)
mostrar("coordenadas_principales", categorias.sort_values("contrib_Dim1_pct", ascending=False))
print("Perfiles agregados:", len(mca["perfiles"]), "| Variables activas:", mca["Q"], "| Categorías:", mca["J"])
print("Validaciones numéricas: inercia total, contribuciones y centrado correctos.")

fig, ax = plt.subplots(figsize=(10,4))
ax.bar(inercia.dimension, inercia.greenacre_pct, label="Inercia Greenacre")
ax.plot(inercia.dimension, inercia.greenacre_acumulada_pct, marker="o", color="#c97036", label="Acumulada")
ax.set(ylabel="Porcentaje", title="Inercia del MCA principal")
ax.legend()
guardar_figura("03_inercia_mca")

comentar(
    f"**Dimensionalidad.** El plano 1–2 recoge **{inercia.cruda_pct.iloc[:2].sum():.1f} % de inercia cruda** "
    f"y **{inercia.greenacre_pct.iloc[:2].sum():.1f} % según Greenacre**. "
    "La corrección no convierte el mapa en una explicación causal ni garantiza que todas sus categorías "
    "estén bien representadas. Para interpretar un punto revisaremos su cos² y su contribución, "
    "incluyendo los ejes 3–4 cuando el primer plano sea insuficiente."
)
comentar(
    "**Decisión para las suplementarias.** Semana, año, variedad, invernadero, grado y corte sirven para "
    "explicar quién ocupa cada perfil, pero no alteran los ejes del MCA principal. Si una categoría aparece "
    "muy alejada, se debe comprobar primero su cos² y su volumen. Si aparece cerca del origen, no hay evidencia "
    "de un perfil propio en este plano. La siguiente decisión analítica es usar semana como activa solo en el "
    "modelo de sensibilidad, porque hacerlo puede repartir la inercia entre 52 niveles y volver menos estable "
    "la lectura del producto y el color."
)
top_contrib=categorias.nlargest(5,"contrib_Dim1_pct")
top_cos=categorias.nlargest(5,"cos2_plano")
comentar(
    "**Lectura ejecutiva del mapa principal.** Las categorías que más construyen Dim1 son "
    + ", ".join(f"{r.variable}={r.categoria}" for _,r in top_contrib.iterrows())
    + ". Las categorías mejor representadas en el plano son "
    + ", ".join(f"{r.variable}={r.categoria}" for _,r in top_cos.iterrows())
    + ". Para gerencia, la primera lista indica qué perfiles explican la separación del mapa; la segunda "
    + "indica dónde la lectura del plano es confiable. Una categoría cercana al origen no es necesariamente "
    + "irrelevante: puede ser frecuente y poco diferenciadora. La acción recomendada es priorizar las categorías "
    + "con alta contribución y cos², y consultar la tabla completa antes de intervenir sobre las demás."
)
''')
md('''### 3.1. Mapas y significado de los ejes

**Contribución:** cuánto ayuda una categoría a construir un eje. **cos²:** qué parte de su distancia al origen se representa en el plano. Un punto lejano con cos² bajo en el plano elegido no debe interpretarse solo por su apariencia. Solo se rotulan las categorías más contribuyentes para evitar un mapa ilegible; todas se exportan a Excel.

El signo de los ejes es arbitrario. Cercanía entre categorías de variables distintas sugiere perfiles relacionados, pero no prueba una relación causal ni una equivalencia entre categorías.
''')
code('''def mapa_mca(modelo, titulo, nombre, ejes=(0,1)):
    if len(modelo["eig"]) <= max(ejes):
        print("No hay dimensiones suficientes para este plano.")
        return
    x,y=ejes
    cat=mp.resultados_categorias(modelo)
    paleta=dict(zip(modelo["activas"], sns.color_palette("colorblind", len(modelo["activas"]))))
    fig,ax=plt.subplots(figsize=(12,8))
    ax.axhline(0,color="gray",linewidth=.6); ax.axvline(0,color="gray",linewidth=.6)
    etiquetas=[]
    for variable,color in paleta.items():
        sub=cat.loc[cat.variable.eq(variable)]
        ax.scatter(sub[f"Dim{x+1}"],sub[f"Dim{y+1}"],s=25+sub.masa_pct*30,
                   alpha=.55,label=variable,color=color)
        score=sub[f"contrib_Dim{x+1}_pct"]+sub[f"contrib_Dim{y+1}_pct"]
        for _,row in sub.loc[score.nlargest(5).index].iterrows():
            etiquetas.append((row[f"Dim{x+1}"],row[f"Dim{y+1}"],row.categoria))
    mp.etiquetar_mapa(ax,etiquetas)
    ax.set(title=titulo, xlabel=f"Dim{x+1} · {modelo['inercia_greenacre_pct'][x]:.1f}% Greenacre",
           ylabel=f"Dim{y+1} · {modelo['inercia_greenacre_pct'][y]:.1f}% Greenacre")
    ax.legend(title="Variable activa")
    guardar_figura(nombre)

mapa_mca(mca,"GAITANA · Perfil productivo histórico", "04_mapa_principal")
mapa_mca(mca,"GAITANA · Perfil productivo: dimensiones 3 y 4", "05_mapa_dimensiones_3_4",(2,3))

aportes = categorias.groupby("variable")[[f"contrib_Dim{k+1}_pct" for k in range(min(4,n))]].sum()
mostrar("aportes_variables", aportes.reset_index())
for eje in [1,2]:
    col=f"contrib_Dim{eje}_pct"
    top=categorias.nlargest(5,col)
    comentar(
        f"**Dimensión {eje}.** La variable que más contribuye es **{aportes[col].idxmax()} "
        f"({aportes[col].max():.1f} %)**. Las categorías que más construyen el eje son "
        + "; ".join(f"**{r.variable}={r.categoria}** ({r[col]:.1f} %)" for _,r in top.iterrows())
        + ". Estos nombres describen el contraste del catálogo; no son una clasificación de calidad de las flores."
    )
    positivos=categorias.loc[categorias[f"Dim{eje}"]>0].nlargest(3,col)
    negativos=categorias.loc[categorias[f"Dim{eje}"]<0].nlargest(3,col)
    comentar(
        f"**Contraste del eje {eje}.** En el lado positivo destacan "
        + ", ".join(positivos.variable+"="+positivos.categoria)
        + "; en el negativo, "+", ".join(negativos.variable+"="+negativos.categoria)
        + ". El contraste expresa perfiles de coocurrencia. El signo podría invertirse sin cambiar el resultado."
    )
comentar(
    f"**Representación de categorías.** {int((categorias.cos2_plano>=.5).sum())} de {len(categorias)} categorías "
    "tienen al menos la mitad de su distancia al origen representada en el plano 1–2. "
    "Para las demás, la tabla completa y los ejes adicionales son necesarios antes de interpretar cercanías."
)
''')
md('''## 4. Grado, corte, variedad y año como información suplementaria

La proyección usa los perfiles de las filas que pertenecen a cada categoría, ponderados por tallos. Una categoría suplementaria no aporta a la inercia del ajuste principal. Se mantienen todas las variedades en la tabla, aunque solo unas pocas se rotulen en un gráfico.
''')
code('''suplementarias = pd.concat([
    mp.proyectar_suplementaria(base_mca,mca,col) for col in SUPLEMENTARIAS
], ignore_index=True)
mostrar("suplementarias", suplementarias, n=15)
mostrar("grados_proyectados", suplementarias.loc[suplementarias.variable.eq("K_grado")])
mostrar("anios_proyectados", suplementarias.loc[suplementarias.variable.eq("K_anio")])

fig,axes=plt.subplots(1,2,figsize=(13,5))
for ax,var in zip(axes,["K_grado","K_anio"]):
    sub=suplementarias.loc[suplementarias.variable.eq(var)]
    ax.axhline(0,color="gray",lw=.6);ax.axvline(0,color="gray",lw=.6)
    ax.scatter(sub.Dim1,sub.Dim2,s=40+150*sub.tallos/sub.tallos.max(),alpha=.7)
    for _,r in sub.iterrows():ax.annotate(r.categoria,(r.Dim1,r.Dim2),xytext=(4,4),textcoords="offset points",fontsize=8)
    ax.set(title=f"Proyección suplementaria: {var}",xlabel="Dim1",ylabel="Dim2")
guardar_figura("06_grado_anio_suplementarios")

comentar(
    "**Cómo leer estas proyecciones.** Si un grado aparece hacia el mismo lado que un producto o color, "
    "sus filas comparten parte del perfil descrito por ese eje. Eso no demuestra una relación causal. "
    "La posición de **SIN_DATO** informa sobre el registro, no sobre la flor. Las diferencias entre años "
    "también pueden reflejar cambios de catálogo, cobertura o criterios comerciales. "
    "Variedad e invernadero se conservan como detalle suplementario para investigar esas diferencias."
)
''')
md('''## 5. Semana ISO: trayectoria temporal y comparación entre años

La semana es una categoría **ordenada y cíclica**: después de la última semana del año viene la primera. El MCA ordinario no usa esa distancia temporal. Por eso la semana se proyecta sin construir los ejes y después se presenta en su orden cronológico. La línea entre semanas es una ayuda de lectura; no es un ajuste ni una trayectoria de individuos.

La semana 53 se conserva cuando existe. Para comparar años se utilizan semanas comunes: la misma etiqueta ISO no equivale siempre a las mismas fechas de fiestas o decisiones comerciales.
''')
code('''semanas_proyectadas=suplementarias.loc[suplementarias.variable.eq("K_semana")].sort_values("categoria")
mostrar("semanas_proyectadas",semanas_proyectadas,n=12)
fig,axes=plt.subplots(1,2,figsize=(14,5))
sem_num=semanas_proyectadas.categoria.str[1:].astype(int)
axes[0].plot(semanas_proyectadas.Dim1,semanas_proyectadas.Dim2,alpha=.35,color="gray")
pts=axes[0].scatter(semanas_proyectadas.Dim1,semanas_proyectadas.Dim2,c=sem_num,cmap="viridis",s=45)
for (_,r),s in zip(semanas_proyectadas.iterrows(),sem_num):
    if s%4==1 or s==sem_num.max():axes[0].annotate(r.categoria,(r.Dim1,r.Dim2),fontsize=8)
fig.colorbar(pts,ax=axes[0],label="Semana ISO")
axes[0].set(title="Semanas proyectadas en el MCA",xlabel="Dim1",ylabel="Dim2")
axes[1].plot(sem_num,semanas_proyectadas.Dim1,label="Dim1",marker=".")
axes[1].plot(sem_num,semanas_proyectadas.Dim2,label="Dim2",marker=".")
axes[1].set(title="Coordenadas en orden cronológico",xlabel="Semana ISO",ylabel="Coordenada suplementaria")
axes[1].legend()
guardar_figura("07_trayectoria_semanal")

# Comparar el mismo año-semana, sin mezclar años en un único punto.
base_mca["K_anio_semana"]=(base_mca.anio.astype(str)+"-S"+base_mca.semana.astype(str).str.zfill(2)).astype("category")
proyeccion_anual=mp.proyectar_suplementaria(base_mca,mca,"K_anio_semana")
proyeccion_anual["anio"]=proyeccion_anual.categoria.str[:4].astype(int)
proyeccion_anual["semana"]=proyeccion_anual.categoria.str[-2:].astype(int)
mostrar("proyeccion_anio_semana",proyeccion_anual,n=12)
fig,axes=plt.subplots(1,2,figsize=(14,5))
for year,sub in proyeccion_anual.groupby("anio"):
    sub=sub.sort_values("semana")
    for ax,dim in zip(axes,["Dim1","Dim2"]):ax.plot(sub.semana,sub[dim],label=str(year),alpha=.8)
for ax,dim in zip(axes,["Dim1","Dim2"]):
    ax.set(title=f"Trayectoria por año · {dim}",xlabel="Semana ISO",ylabel="Coordenada suplementaria")
    ax.legend(ncol=2)
guardar_figura("08_trayectorias_por_anio")
comentar(
    "**Lectura temporal.** La curva conjunta indica cómo cambia el perfil promedio a lo largo del calendario. "
    "Las curvas por año permiten comprobar si esa forma se repite o si la produce un año particular. "
    "Una curva suave en el promedio no basta para afirmar estacionalidad: puede resultar de cobertura desigual "
    "o de cambios del catálogo. La siguiente sección contrasta directamente las curvas de participación por producto."
)
''')
md('''### 5.1. ¿Se repite la composición semanal de productos?

Se calcula la proporción de tallos de cada producto dentro de cada año-semana. Esto separa **composición** de **volumen total**. Se usa el tramo contiguo más largo de semanas comunes a todos los años seleccionados; no se compara un año completo con 2026 parcial.

Para cada producto se calcula la correlación de sus curvas entre cada par de años y se promedia. Se excluyen pares con curvas constantes. Una correlación positiva indica movimientos semanales concordantes; no demuestra igualdad de volúmenes ni permite pronosticar por sí sola.

Como comprobación exploratoria se desplaza circularmente cada curva anual 199 veces, manteniendo su forma y cambiando su alineación con el calendario. Se compara la concordancia observada con esas alineaciones y se corrige por productos con FDR de Benjamini–Hochberg. Esta referencia supone intercambiabilidad de la fase temporal: no controla cambios de catálogo, cobertura incompleta dentro de una semana ni decisiones comerciales. El resultado se limita al tramo común, y **no prueba un ciclo anual completo**.
''')
code('''recurrencia, participacion_semanal, semanas_comunes = mp.recurrencia_semanal(base_mca,199,SEMILLA)
mostrar("recurrencia_productos",recurrencia,n=30)
if not recurrencia.empty:
    top_productos=recurrencia.head(4).producto.tolist()
    fig,axes=plt.subplots(2,2,figsize=(14,9),squeeze=False)
    for ax,producto in zip(axes.flat,top_productos):
        for year in sorted(base_mca.anio.unique()):
            serie=participacion_semanal.loc[year,producto].reindex(semanas_comunes)
            ax.plot(serie.index,100*serie,label=str(year),alpha=.8)
        ax.set(title=producto,xlabel="Semana ISO",ylabel="% del volumen semanal")
        ax.legend(ncol=3,fontsize=8)
    for ax in list(axes.flat)[len(top_productos):]:ax.set_visible(False)
    guardar_figura("09_recurrencia_productos")
    primera=recurrencia.iloc[0]
    evidencia=recurrencia.loc[(recurrencia.correlacion_media>0)&(recurrencia.q_FDR<=.05)]
    comentar(
        f"**Recurrencia observada.** Se compararon **{len(semanas_comunes)} semanas comunes**, "
        f"de la **{min(semanas_comunes)} a la {max(semanas_comunes)}**. "
        f"La mayor concordancia corresponde a **{primera.producto}**, con correlación media "
        f"**{primera.correlacion_media:.3f}** y **q FDR = {primera.q_FDR:.3f}**. "
        f"**{len(evidencia)} productos** tienen correlación positiva y q ≤ 0,05 frente a los desplazamientos. "
        "Los restantes no muestran esa evidencia bajo este contraste; no equivale a demostrar ausencia de estacionalidad. "
        "Antes de usar estos patrones para planear, deben comprobarse en años reservados y con cobertura comparable."
    )
else:
    comentar("**Recurrencia no estimable:** no hay suficientes años, semanas comunes contiguas o curvas variables. No se fuerza una conclusión temporal.")
''')
md('''### 5.2. ¿Se repite la forma del volumen semanal?

Aquí se repite el contraste con **tallos por producto y semana**, sin dividir entre el total de la finca. Para graficar, cada curva se expresa como índice: `100 × tallos de la semana / promedio de ese producto-año en las semanas comunes`. Un índice 120 significa 20 % por encima de ese promedio.

La correlación mide semejanza de la forma temporal aunque la escala de producción cambie entre años. Un producto sin volumen en todo el tramo no tiene índice definido y no aporta un par válido. También se muestra el volumen total de la finca en orden semanal, para distinguir un cambio general de producción de uno específico de producto. Los contrastes FDR de volumen forman una familia exploratoria distinta de los de composición.
''')
code('''recurrencia_volumen, indice_volumen, semanas_volumen = mp.recurrencia_semanal(
    base_mca,199,SEMILLA,modo="volumen"
)
mostrar("recurrencia_volumen",recurrencia_volumen,n=30)
semanal_total=base_mca.groupby(["anio","semana"],observed=True).tallos.sum().reset_index()
mostrar("volumen_semanal_total",semanal_total,n=12)
fig,axes=plt.subplots(1,2,figsize=(14,5))
for year,sub in semanal_total.groupby("anio"):
    sub=sub.sort_values("semana")
    axes[0].plot(sub.semana,sub.tallos/1e6,label=str(year),alpha=.85)
axes[0].set(title="Producción total de GAITANA",xlabel="Semana ISO",ylabel="Millones de tallos")
axes[0].legend(ncol=2)
if not recurrencia_volumen.empty:
    producto=recurrencia_volumen.iloc[0].producto
    for year in sorted(base_mca.anio.unique()):
        serie=indice_volumen.loc[year,producto].reindex(semanas_volumen)
        axes[1].plot(serie.index,100*serie,label=str(year),alpha=.85)
    axes[1].axhline(100,color="gray",ls="--",lw=.8)
    axes[1].set(title=f"Forma del volumen semanal · {producto}",xlabel="Semana ISO",ylabel="Índice: promedio del tramo = 100")
    axes[1].legend(ncol=2)
    mejor_volumen=recurrencia_volumen.iloc[0]
    significativos_volumen=recurrencia_volumen.loc[(recurrencia_volumen.correlacion_media>0)&(recurrencia_volumen.q_FDR<=.05)]
    comentar(
        f"**Volumen semanal.** La mayor concordancia corresponde a **{producto}** "
        f"(correlación media **{mejor_volumen.correlacion_media:.3f}**; q FDR **{mejor_volumen.q_FDR:.3f}**). "
        f"**{len(significativos_volumen)} productos** tienen correlación positiva y q ≤ 0,05. "
        "Este resultado se refiere a la forma de los volúmenes en el tramo común. "
        "Las discrepancias entre volumen y participación ayudan a distinguir variación propia del producto "
        "de cambios del total de la finca; ninguna de las dos pruebas identifica por sí sola su causa."
    )
else:
    axes[1].set_visible(False)
    comentar("No hay suficientes curvas para evaluar recurrencia de volumen.")
guardar_figura("09b_recurrencia_volumen")
''')

md('''## 6. MCA del grado comercial y análisis de sensibilidad

El segundo MCA añade `grado` como activo únicamente donde está informado. Antes del ajuste se presenta qué porcentaje de producción representa esta subbase por año. No se asume que `GRANEL`, cintas o `NACIONAL` formen una escala universal de calidad: los nombres describen clasificaciones registradas.

Se revisa la relación producto–grado para detectar categorías casi deterministas. Una coincidencia fuerte puede describir la política de clasificación de un producto; no demuestra un defecto de calidad.
''')
code('''base_grado=base_mca.loc[base_mca["K_grado_sin_agrupar"].ne("SIN_DATO")].copy()
cobertura_grado=base_mca.groupby("anio").tallos.sum().to_frame("tallos_totales")
cobertura_grado["tallos_grado_conocido"]=base_grado.groupby("anio").tallos.sum()
cobertura_grado["cobertura_grado_pct"]=100*cobertura_grado.tallos_grado_conocido.fillna(0)/cobertura_grado.tallos_totales
mostrar("cobertura_grado",cobertura_grado.reset_index())
mca_grado=mp.ajustar_mca(base_grado,ACTIVAS+["K_grado"])
categorias_grado=mp.resultados_categorias(mca_grado)
mostrar("coordenadas_mca_grado",categorias_grado.sort_values("contrib_Dim1_pct",ascending=False))
mapa_mca(mca_grado,"GAITANA · MCA con grado conocido", "10_mca_grado")

tabla_pg=mp.tabla_pesos(base_grado,"K_producto","K_grado")
perfiles_grado=100*tabla_pg.div(tabla_pg.sum(axis=1),axis=0)
mostrar("grado_por_producto",perfiles_grado.reset_index())
dominancia=pd.DataFrame({"grado_dominante":perfiles_grado.idxmax(axis=1),
                         "porcentaje_dominante":perfiles_grado.max(axis=1),"tallos":tabla_pg.sum(axis=1)})
mostrar("dominancia_grado",dominancia.sort_values("porcentaje_dominante",ascending=False).reset_index())
aporte_grado=categorias_grado.loc[categorias_grado.variable.eq("K_grado"),["contrib_Dim1_pct","contrib_Dim2_pct"]].sum()
comentar(
    f"**Grado comercial.** Esta subbase representa **{100*base_grado.tallos.sum()/base_mca.tallos.sum():.1f} %** "
    f"de los tallos del análisis principal. El grado aporta **{aporte_grado.iloc[0]:.1f} % a Dim1** y "
    f"**{aporte_grado.iloc[1]:.1f} % a Dim2** de este segundo ajuste. "
    "La tabla producto–grado permite comprobar si el mapa está destacando una clasificación casi exclusiva "
    "de un producto. No se atribuye esa asociación al manejo agronómico ni se supone un destino comercial "
    "que el archivo no documenta."
)
''')
md('''### 6.1. ¿El resultado depende de una decisión del análisis?

Se comparan: semana como activa, mismo peso por registro, producto–grado–semana como activas y MCA comercial sin STATICE. El principal conserva todos los productos; retirar STATICE es únicamente una prueba de sensibilidad. Los ejes de ajustes distintos no son intercambiables: se comparan sus variables contribuyentes y la cobertura, no el signo o la distancia de un punto entre mapas.
''')
code('''sensibilidad=[]
def registrar_modelo(nombre,df,activas,peso="tallos"):
    modelo=mp.ajustar_mca(df,activas,peso=peso)
    cat=mp.resultados_categorias(modelo)
    contrib=cat.groupby("variable")[["contrib_Dim1_pct","contrib_Dim2_pct"]].sum()
    sensibilidad.append({"modelo":nombre,"registros":len(df),"tallos":df.tallos.sum(),
        "variables":", ".join(modelo["activas"]),"plano_crudo_pct":sum(modelo["inercia_cruda_pct"][:2]),
        "plano_greenacre_pct":sum(modelo["inercia_greenacre_pct"][:2]),
        "mayor_aporte_Dim1":contrib.contrib_Dim1_pct.idxmax(),
        "aporte_semana_Dim1_pct":contrib.loc["K_semana","contrib_Dim1_pct"] if "K_semana" in contrib.index else np.nan,
        "aporte_grado_Dim1_pct":contrib.loc["K_grado","contrib_Dim1_pct"] if "K_grado" in contrib.index else np.nan})
    return modelo

registrar_modelo("Principal",base_mca,ACTIVAS)
mca_semana=registrar_modelo("Semana activa",base_mca,ACTIVAS+["K_semana"])
base_mca["peso_registro"]=1
registrar_modelo("Peso igual por registro",base_mca,ACTIVAS,"peso_registro")
registrar_modelo("Producto, grado y semana",base_grado,["K_producto","K_grado","K_semana"])
registrar_modelo("Grado activo",base_grado,ACTIVAS+["K_grado"])
sin_statice=base_grado.loc[base_grado.K_producto_sin_agrupar.ne("STATICE")]
if len(sin_statice) and len(sin_statice)<len(base_grado):
    registrar_modelo("Grado activo sin STATICE",sin_statice,ACTIVAS+["K_grado"])
sensibilidad=pd.DataFrame(sensibilidad)
mostrar("sensibilidad",sensibilidad)
mostrar("semana_activa_coordenadas",mp.resultados_categorias(mca_semana))
sem_act=sensibilidad.loc[sensibilidad.modelo.eq("Semana activa")].iloc[0]
comentar(
    f"**Semana activa.** Aporta **{sem_act.aporte_semana_Dim1_pct:.1f} % a Dim1** y el plano 1–2 "
    f"recoge **{sem_act.plano_crudo_pct:.1f} % de inercia cruda** en ese ajuste. "
    "Esto mide cuánto participa en los ejes cuando se le permite construirlos, no el porcentaje de "
    "producción explicado por el calendario. La comparación por registros cambia la pregunta: "
    "describe el registro típico, mientras el ajuste ponderado describe la distribución de los tallos."
)
''')
md('''### 6.2. MCA con imputación y todos los registros: sensibilidad

Se incorpora `grado_analisis` con sus predicciones identificadas y su categoría `SIN_REFERENCIA`. Este ajuste incluye todos los registros de la base MCA, también los que no tienen grado observado. Se compara con los modelos anteriores; la subbase de grado observado permanece como referencia para describir porcentajes comerciales sin mezclar predicciones.

`SIN_REFERENCIA` puede construir un eje por ausencia histórica de información. Se reporta su contribución y se evita interpretarla como un grado real. **Imputar por producto y variedad también puede reforzar artificialmente su asociación con el grado.** El ajuste se presenta como sensibilidad, no como evidencia independiente ni como reconstrucción confirmada de 2021.
''')
code('''base_mca["K_grado_imputado"]=base_mca.grado_analisis.replace({"NAC":"NACIONAL", "NA":"NACIONAL"})
base_mca["K_corte_imputado"]=base_mca.tipo_corte_analisis
mca_imputado=mp.ajustar_mca(base_mca, ACTIVAS+["K_grado_imputado"])
cat_imputado=mp.resultados_categorias(mca_imputado)
mostrar("mca_grado_imputado", cat_imputado.sort_values("contrib_Dim1_pct", ascending=False))
mapa_mca(mca_imputado,"GAITANA · Grado imputado y faltantes conservados", "10b_mca_grado_imputado")
mostrar("corte_imputado_suplementario", mp.proyectar_suplementaria(base_mca,mca_imputado,"K_corte_imputado"))
sin_ref=cat_imputado.loc[cat_imputado.variable.eq("K_grado_imputado") & cat_imputado.categoria.eq("SIN_REFERENCIA")]
aporte_sin_ref=float(sin_ref.contrib_Dim1_pct.sum())
comentar(
    f"**MCA sin eliminar faltantes.** Este ajuste incluye **{len(base_mca):,} registros**, "
    f"el **100 % de los {base_mca.tallos.sum():,.0f} tallos** de la base MCA. "
    f"SIN_REFERENCIA aporta **{aporte_sin_ref:.1f} % a Dim1**. "
    "Los porcentajes comerciales de la siguiente sección se calculan únicamente con grados observados; "
    "las filas sin grado siguen disponibles en la base general y en este ajuste."
)
''')
md('''## 7. Producto y grado: detalle por variedad y año

Se aísla la tabla producto–grado y se realiza un análisis de correspondencias simple. Se reporta V de Cramér como tamaño descriptivo de asociación, sin usar p-valores basados en independencia entre tallos.

Después se comparan porcentajes de **no GRANEL** por variedad dentro de cada producto y año. Esta definición es operativa: “no GRANEL” no significa automáticamente peor calidad, ni pérdida, ni menor precio. Separar por producto y año reduce dos mezclas relevantes, pero no controla semana, bloque o política comercial.
''')
code('''tabla_producto_grado=mp.tabla_pesos(base_grado,"K_producto","K_grado")
ac=mp.ajustar_ac(tabla_producto_grado)
mostrar("producto_grado_tallos",tabla_producto_grado.reset_index())
mostrar("producto_grado_porcentaje",(100*tabla_producto_grado.div(tabla_producto_grado.sum(axis=1),axis=0)).reset_index())
if len(ac["eig"])>=2:
    fig,ax=plt.subplots(figsize=(12,8))
    ax.axhline(0,color="gray",lw=.6);ax.axvline(0,color="gray",lw=.6)
    etiquetas_ac=[]
    for coord,nombres,marker,label in [(ac["coords_filas"],ac["filas"],"o","Producto"),
                                     (ac["coords_columnas"],ac["columnas"],"D","Grado")]:
        ax.scatter(coord[:,0],coord[:,1],marker=marker,alpha=.65,label=label)
        # Rotular los grados y los productos más alejados, sin ocultar puntos.
        indices=range(len(nombres)) if label=="Grado" else np.argsort(np.sum(coord[:,:2]**2,axis=1))[-10:]
        for i in indices:etiquetas_ac.append((coord[i,0],coord[i,1],str(nombres[i])))
    mp.etiquetar_mapa(ax,etiquetas_ac)
    ax.set(title="AC descriptivo · Producto y grado conocido",xlabel=f"Dim1 ({ac['inercia_pct'][0]:.1f} %)",
           ylabel=f"Dim2 ({ac['inercia_pct'][1]:.1f} %)")
    ax.legend();guardar_figura("11_ac_producto_grado")

base_grado["tallos_no_granel"]=base_grado.tallos.where(base_grado.K_grado_sin_agrupar.ne("GRANEL"),0)
variedad_producto=base_grado.groupby(["anio","K_producto","K_variedad"],observed=True).agg(
    tallos=("tallos","sum"),tallos_no_granel=("tallos_no_granel","sum"),
    semanas=("semana","nunique")
).reset_index()
variedad_producto["no_granel_pct"]=100*variedad_producto.tallos_no_granel/variedad_producto.tallos
mostrar("variedad_producto_anio",variedad_producto.sort_values("tallos",ascending=False))
comparables=variedad_producto.loc[(variedad_producto.tallos>=100_000)&(variedad_producto.semanas>=12)]
contrastes=comparables.groupby(["anio","K_producto"],observed=True).agg(
    variedades=("K_variedad","nunique"),minimo_pct=("no_granel_pct","min"),maximo_pct=("no_granel_pct","max")
).reset_index()
contrastes=contrastes.loc[contrastes.variedades>=2].copy()
contrastes["rango_pp"]=contrastes.maximo_pct-contrastes.minimo_pct
mostrar("contrastes_variedad",contrastes.sort_values("rango_pp",ascending=False))
comentar(
    f"**Asociación producto–grado.** V de Cramér es **{ac['V']:.3f}** en los tallos con grado conocido. "
    f"Hay **{len(contrastes)} combinaciones año–producto** con al menos dos variedades que cumplen "
    "100.000 tallos y 12 semanas observadas. Sus diferencias se expresan en puntos porcentuales, "
    "sin cocientes inestables cuando una variedad tiene 0 %. Aun dentro del mismo producto y año, "
    "las semanas efectivamente cosechadas y la política comercial pueden explicar parte de la diferencia. "
    "Por tanto, el resultado orienta una revisión operativa; no demuestra un efecto causal de la variedad."
)
''')
md('''## 8. Conclusiones, límites y siguientes comprobaciones

Los siguientes comentarios se construyen con las cifras de esta ejecución. No se asignan significados agronómicos a las cintas ni se califican variedades como buenas o malas sin validar las reglas de clasificación con la empresa.
''')
code('''conclusiones=[
    f"**Base y alcance.** {len(prod):,} registros limpios de GAITANA; {len(base_mca):,} evaluados "
    f"en el MCA, entre {base_mca.fecha_corte.min().date()} y {base_mca.fecha_corte.max().date()}. "
    "La auditoría permite reconstruir los libros y hojas utilizados.",
    f"**Estructura productiva.** {aportes.contrib_Dim1_pct.idxmax()} es la variable que más "
    f"construye Dim1 ({aportes.contrib_Dim1_pct.max():.1f} %). El primer plano resume "
    f"{sum(mca['inercia_greenacre_pct'][:2]):.1f} % de inercia Greenacre. Se interpretan contribuciones "
    "y representación de categorías, no una predicción de tallos.",
    f"**Clasificación comercial.** El MCA con grado utiliza {100*base_grado.tallos.sum()/base_mca.tallos.sum():.1f} % "
    "de los tallos como referencia observada. El ajuste de sensibilidad con imputación y SIN_REFERENCIA "
    "conserva el 100 %. Los faltantes históricos limitan comparaciones; no deben leerse como cambios de calidad.",
    f"**Imputación trazable.** Se completan {prod.grado_metodo.eq('referencia_estable_entre_anios').sum():,} "
    "grados adicionales en una columna separada. El traslado histórico del corte se evalúa y puede "
    "descartarse; los valores sin respaldo permanecen identificados sin eliminar sus registros.",
    "**Semana.** Se conserva como categoría ordinal/cíclica para la interpretación cronológica, pero "
    "el MCA estándar la trata nominalmente. La proyección y el contraste entre años complementan el mapa.",
    f"**Producto y grado.** Su asociación descriptiva tiene V={ac['V']:.3f}. El detalle "
    "por variedad y año no controla todas las diferencias de mezcla ni establece causalidad.",
]
if "detalle" in auditoria_2021:
    conclusiones.append(
        f"**Pico de 2021.** La semana {auditoria_2021['semana']} suma "
        f"{auditoria_2021['detalle'].tallos.sum():,.0f} tallos. La auditoría muestra los bloques fuente "
        "y sus coincidencias. La posible copia se mantiene señalada; ningún escenario alternativo "
        "sustituye el dato observado sin confirmar su procedencia."
    )
if not recurrencia.empty:
    mejor=recurrencia.iloc[0]
    conclusiones.append(
        f"**Repetición entre años.** En semanas {min(semanas_comunes)}–{max(semanas_comunes)}, "
        f"{mejor.producto} tiene la mayor correlación media de participación ({mejor.correlacion_media:.3f}; "
        f"q={mejor.q_FDR:.3f}). Es evidencia descriptiva sobre composición en ese tramo, "
        "No se detecta evidencia tras FDR si q supera 0,05; no es una garantía de repetición anual."
    )
if not recurrencia_volumen.empty:
    mejor=recurrencia_volumen.iloc[0]
    conclusiones.append(
        f"**Forma del volumen.** {mejor.producto} tiene la mayor correlación media entre años "
        f"({mejor.correlacion_media:.3f}; q={mejor.q_FDR:.3f}) en el tramo común. "
        "Este contraste complementa la composición, sin confundir un mayor volumen con una curva más repetible."
    )
for texto in conclusiones:comentar(texto)
comentar(
    "**Siguientes comprobaciones.** Validar con la empresa las equivalencias de grados "
    "y los posibles solapamientos entre archivos. Para evaluar capacidad predictiva, "
    "reservar un año y comparar contra una referencia de la misma semana del año anterior. Si se quiere "
    "estudiar diferencias comerciales por variedad, controlar al menos producto y semana; el MCA por sí solo no identifica sus causas."
)
''')
md('''## 9. Exportaciones y referencias

Se exportan las tablas completas, figuras y comentarios. La base limpia y los solapamientos permanecen en `Datos/modelado/mca_produccion`, fuera del historial Git. Los archivos fuente no se modifican.

Referencias metodológicas:
- Lê, Josse y Husson (2008), [FactoMineR: An R Package for Multivariate Analysis](https://www.jstatsoft.org/article/view/v025i01). Separación entre variables activas y suplementarias.
- [Documentación oficial de MCA de FactoMineR](https://search.r-project.org/CRAN/refmans/FactoMineR/html/MCA.html): pesos de filas, coordenadas, contribuciones y cos².
- Greenacre, [Multiple Correspondence Analysis, materiales CARME](https://statmath.wu.ac.at/courses/CAandRelMeth/CARME6_BW.pdf): indicadora, matriz de Burt, puntos suplementarios e inercia ajustada.

El contraste de desplazamientos semanales es una comprobación exploratoria adicional del presente análisis, no una salida del MCA.
''')
code('''ruta_excel=SALIDA / "resultados_mca_gaitana.xlsx"
with pd.ExcelWriter(ruta_excel,engine="openpyxl") as writer:
    for nombre,tabla in TABLAS.items():
        # Las tablas agregadas no requieren truncar filas para exportar.
        tabla.to_excel(writer,sheet_name=nombre[:31],index=False)
        hoja=writer.sheets[nombre[:31]]
        hoja.freeze_panes="A2"
        hoja.auto_filter.ref=hoja.dimensions
        for columna in hoja.columns:
            hoja.column_dimensions[columna[0].column_letter].width=min(48,max(16,len(str(columna[0].value))+2))
texto="# Informe interpretativo · MCA de GAITANA\\n\\n"+"\\n\\n".join(COMENTARIOS)
(SALIDA / "interpretacion_mca_gaitana.md").write_text(texto,encoding="utf-8")
(SALIDA / "parametros.json").write_text(json.dumps({
    "carpeta_fuente":str(CARPETA_PRODUCCION),"finca":"GAITANA", "anios_archivo":ANIOS_ARCHIVO,
    "anios_iso":ANIOS_ISO,"umbral_raro":UMBRAL_RARO,"semilla":SEMILLA,
    "variables_activas":ACTIVAS,"variables_suplementarias":SUPLEMENTARIAS,
    "imputacion":{"llaves":ma.LLAVES,"minimo_registros_anio":30,"minimo_anios":2,
                  "dominancia_minima":.95,"minimo_acierto_validacion":.90,
                  "minimo_evaluables_anio":1000,"sin_referencia":"conservar con etiqueta"},
    "base_auditada":str(CARPETA_CACHE/"produccion_gaitana_auditada.parquet"),
    "registros_limpios":len(prod),"registros_mca":len(base_mca),"tallos_mca":float(base_mca.tallos.sum())
},ensure_ascii=False,indent=2),encoding="utf-8")
print("Resultados:",SALIDA)
display(FileLink(str(ruta_excel.relative_to(Path.cwd())) if ruta_excel.is_relative_to(Path.cwd()) else str(ruta_excel)))
''')

if __name__=='__main__':
    if OUT.exists():
        backup=Path(tempfile.gettempdir())/('05_MCA_2026_antes_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.ipynb')
        shutil.copy2(OUT,backup)
        print('Respaldo:',backup)
    nb=nbf.v4.new_notebook(cells=cells,metadata={
        'kernelspec':{'display_name':'Python (entorno_tesis)','language':'python','name':'python3'},
        'language_info':{'name':'python','version':'3.14.0'}})
    nbf.write(nb,OUT)
    print('Notebook generado:',OUT,'| Celdas:',len(cells))
