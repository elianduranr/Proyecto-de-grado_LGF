from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient

R=Path(__file__).resolve().parents[1]; N=R/"Notebooks"
def M(x): return nbf.v4.new_markdown_cell(x.strip())
def C(x): return nbf.v4.new_code_cell(x.strip())
def guardar(celdas,nombre):
    nb=nbf.v4.new_notebook(cells=celdas); nb.metadata["kernelspec"]={"display_name":"Python 3","language":"python","name":"python3"}
    NotebookClient(nb,timeout=600,kernel_name="python3",resources={"metadata":{"path":str(R)}}).execute(); nbf.write(nb,N/nombre)

inicio="""from pathlib import Path
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from IPython.display import display
RAIZ=Path.cwd(); RAIZ=RAIZ if (RAIZ/'Datos').exists() else RAIZ.parent
base=pd.read_csv(RAIZ/'Datos/modelado/df_modelo_final.csv',low_memory=False)"""
guardar([
 M("""# 00 · Entender una estimación con un solo producto-color

Caso `MINICARNATION · LIGHT PINK`. Aquí se explica una **base analítica y benchmarks**; no existe todavía un modelo final entrenado. La teoría nace de `plantas por segmento × curva variedad-edad`."""),
 C(inicio+"""
q=base[(base.k_producto=='MINICARNATION')&(base.k_color=='LIGHT PINK')]
ultima=q.loc[q.estado_objetivo.eq('real_observado'),'lunes_objetivo'].max()
ej=q[(q.lunes_objetivo==ultima)&(q.horizonte==1)].copy()
print('Semana:',ultima,'| filas:',len(ej))"""),
 M("""## 1. Plano y curva

`segmentos_plan` cuenta registros productivos y `camas_plan_unicas` camas físicas. Edad y curva descriptiva están ponderadas por plantas. La fórmula oficial sigue aplicándose por segmento; una curva ausente nunca se vuelve cero."""),
 C("""display(ej[['k_variedad','plantas','segmentos_plan','camas_plan_unicas','edad_media_ponderada','edad_min','edad_max','flores_planta_media_ponderada','curva_iqr_media_ponderada','cobertura_curva_pct','tallos_teoricos']].sort_values('tallos_teoricos',ascending=False))"""),
 M("""## 2. Tres referencias

Persistencia usa el último real estrictamente anterior a la emisión. El residuo recomendado es `real - teórico`; un futuro ajuste será `teórico + residuo predicho`."""),
 C("""r=pd.DataFrame({'metodo':['Curva','Ingeniero','Persistencia','Real'],'tallos':[ej.tallos_teoricos.sum(min_count=1),ej.tallos_ingeniero.sum(min_count=1),ej.tallos_persistencia.sum(min_count=1),ej.tallos_reales.sum(min_count=1)]}); real=r.loc[r.metodo.eq('Real'),'tallos'].iloc[0]; r['residuo_real_menos_pronostico']=np.where(r.metodo.eq('Real'),np.nan,real-r.tallos); display(r); r.plot.bar(x='metodo',y='tallos',legend=False,figsize=(8,4)); plt.tight_layout(); plt.show()"""),
 M("""## 3. Estados y disponibilidad

`estado_objetivo` distingue observado, futuro y semana cerrada sin registro. Clima `*_lagN_seguro` puede ser predictor; `*_emision_condicionado` requiere confirmación; `*_objetivo_prohibido` nunca entra al entrenamiento."""),
 C("""display(q.groupby(['horizonte','estado_objetivo']).size().rename('filas').reset_index()); display(pd.read_csv(RAIZ/'Datos/modelado/metricas_benchmarks_comunes.csv'))"""),
 M("""## Límites

No se conoce aún la definición definitiva de H1, disponibilidad de producción anterior, clima de emisión, curvas ni correcciones del ingeniero. Esta comparación no demuestra causalidad ni representa un modelo entrenado.""")
],"00_entendimiento del estimado.ipynb")

guardar([
 M("""# 02 · Base analítica productiva y benchmarks

`Planos + Curvas + clima disponible → futura corrección del teórico`. Ingeniero y persistencia son benchmarks. **No se entrena todavía un modelo final.**"""),
 C(inicio+"""
MOD=RAIZ/'Datos/modelado'; AUD=MOD/'auditoria'; metricas=pd.read_csv(MOD/'metricas_benchmarks_comunes.csv')
print('Base:',base.shape); display(pd.read_csv(AUD/'resumen_revision_modelo02.csv'))"""),
 M("""## 1. Definición y estados

`residuo_teorico = tallos_reales - tallos_teoricos`; `pronostico_corregido = tallos_teoricos + residuo_predicho`. H1=emisión y `semanas_adelante=0`, decisión todavía provisional."""),
 C("""llave=['anio_emision','semana_emision','anio_objetivo','semana_objetivo','horizonte','k_producto','k_color','k_variedad']; print('Duplicados:',base.duplicated(llave).sum()); display(base.groupby(['anio_objetivo','horizonte','estado_objetivo']).size().rename('filas').reset_index().head(25))"""),
 M("""## 2. Plano y curvas

Solo se eliminan duplicados exactos. Se distinguen segmentos y camas físicas; se conservan edad ponderada, rango, dispersión, cobertura, observaciones, camas piloto e IQR. La disponibilidad de curvas dentro del año no está fechada."""),
 C("""display(base[['plantas','segmentos_plan','camas_plan_unicas','edad_media_ponderada','edad_min','edad_max','edad_desviacion','flores_planta_media_ponderada','curva_iqr_media_ponderada','cobertura_curva_pct']].describe().T); display(pd.read_csv(AUD/'resumen_duplicados_planos.csv').tail())"""),
 M("""## 3. Clima sin fuga

Seguro: `*_lag1_seguro` a `*_lag4_seguro`. Condicionado: `*_emision_condicionado`. Prohibido: `*_objetivo_prohibido`. Las semanas ISO inválidas se aíslan, no se reasignan."""),
 C("""display(pd.read_csv(AUD/'resumen_calidad_clima.csv')); display(pd.read_csv(AUD/'clima_semanas_iso_invalidas.csv')); display(pd.DataFrame({'grupo':['seguro','condicionado','prohibido'],'columnas':[sum(c.endswith('_seguro') for c in base),sum(c.endswith('_emision_condicionado') for c in base),sum(c.endswith('_objetivo_prohibido') for c in base)]}))"""),
 M("""## 4. Benchmark común

Curva, ingeniero y persistencia se evalúan exactamente sobre las mismas filas observadas y se reporta cobertura."""),
 C("""display(metricas); import seaborn as sns; sns.lineplot(data=metricas,x='horizonte',y='WAPE_pct',hue='metodo',marker='o'); plt.title('WAPE sobre pares comunes'); plt.tight_layout(); plt.show()"""),
 M("""Persistencia nunca usa la emisión ni una semana posterior. Su validez depende de que el real anterior ya estuviera disponible al emitir."""),
 M("""## 5. Validación temporal

No se usa división aleatoria. Los cortes separan semanas objetivo completas: 2023→2024, 2023–2024→2025 y 2023–2025→2026 como prueba final."""),
 C("""display(pd.read_csv(MOD/'cortes_validacion_temporal.csv')); display(pd.read_csv(AUD/'validacion_final.csv'))"""),
 M("""## 6. Clima y residuo

Las correlaciones son exploratorias, no causales. Deben controlarse variedad, edad, estacionalidad, labores y rezagos."""),
 C("""s=base.query(\"horizonte==1 and estado_objetivo=='real_observado'\").groupby(['anio_emision','semana_emision'],as_index=False).agg(residuo=('residuo_teorico','sum'),real=('tallos_reales','sum'),temp=('temp_media_lag1_seguro','first'),humedad=('humedad_media_lag1_seguro','first'),lluvia=('lluvia_acumulada_lag1_seguro','first'),radiacion=('radiacion_media_lag1_seguro','first')); display(s[['temp','humedad','lluvia','radiacion','residuo','real']].corr(method='spearman').loc[['temp','humedad','lluvia','radiacion'],['residuo','real']])"""),
 M("""## 7. Decisiones abiertas

Definición de H1, hora de emisión, clima disponible, significado del real ausente, tallos exportables, fecha de curvas, fecha de versiones corregidas y papel del modelo. Consultar `DECISIONES_PENDIENTES_TUTOR.md`.""")
],"02.ipynb")
print("Notebooks actualizados y ejecutados")
