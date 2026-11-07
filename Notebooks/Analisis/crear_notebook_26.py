"""Construye el cuaderno ejecutable de evaluación local; no contiene resultados inventados."""
from pathlib import Path
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[2]
cells=[]
def md(s):cells.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s):cells.append(nbf.v4.new_code_cell(s.strip()))

md('''# 26. Validación temporal actualizada y reentrenamiento en operación

Se conserva el modelo del cuaderno 19: boosting sin clima, grupos H1–H2/H3–H5 y corrección de teoría o Media4. No se buscan nuevos parámetros. Esta ejecución **local y retrospectiva** usa una copia identificada de las fuentes; no publica pronósticos ni escribe en SQL. La consulta de WebFlor y la persistencia SQL son procesos separados: este cuaderno puede repetirse con los archivos ya archivados, sin volver a consultar la empresa.

Respondemos tres preguntas: ¿los datos nuevos están incorporados?, ¿cómo se comporta la configuración fija después de S36?, ¿qué diferencia hay entre conservar un ajuste congelado y reentrenarlo mensualmente? No equiparamos esta simulación con un pronóstico emitido antes de la cosecha.

Orden: fuentes → separación temporal → modelo fijado → entrenamiento/prueba → comparación nominal con ingeniero → diagnóstico y pronóstico más reciente → conclusiones y operación.''')
code(r'''
from pathlib import Path
import sys,json,hashlib,joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from threadpoolctl import threadpool_limits
ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'plataforma_gaitana/backend/app/model19.py').exists())
sys.path.insert(0,str(ROOT/'plataforma_gaitana/backend'))
from app.model19 import dataset,build_model,CATEGORIES,MEMORY,WEATHER,PARAMS
from app.history_eval import engineer_archive
from app.data import KEY
SOURCE=ROOT/'plataforma_gaitana/storage/datasets/evaluacion_local_20261028'
OUT=ROOT/'Datos_analiticos_proyecto/validacion_temporal_20261028'
OUT.mkdir(exist_ok=True);(OUT/'figuras').mkdir(exist_ok=True)
AS_OF=pd.Timestamp('2026-10-28')
NEW_START=pd.Timestamp('2026-09-07')
FROZEN_CUT=pd.Timestamp('2026-08-03')
MANIFEST=json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8'))
assert MANIFEST['offline'] and MANIFEST['state'] in ['validado_local','validado','activo']
assert len(set(MANIFEST['completed_stages']))==11
print('Copia local:',MANIFEST['id'],'· fecha de evaluación:',AS_OF.date())
print('Parámetros conservados:',PARAMS)
''')
md('''## 1. Qué datos usamos y qué validamos

La base persistida anterior llega al 24/10. Se incorporan los Excel recibidos de clima y plano S42 y la descarga WebFlor ya archivada hasta el 27/10. La ventana WebFlor sustituye sólo su rango reciente, preservando el histórico anterior y los movimientos repetidos legítimos. No se consulta la empresa en esta corrida.

Se comprueban hashes, columnas y cantidades mediante el ETL canónico. La producción actualizada de una semana en curso **no la convierte en objetivo evaluable**: evaluamos sólo semanas terminadas antes del 28/10. Los estimados nominales del ingeniero se usan exclusivamente como referencia, nunca como entradas.''')
code(r'''
source_rows=[]
for name,item in MANIFEST['outputs'].items():
    path=SOURCE/'Datos_analiticos_proyecto'/f'{name}.parquet'
    h=hashlib.sha256(path.read_bytes()).hexdigest()
    assert h==item['sha256'],name
    source_rows.append({'fuente':name,'registros':item['rows'],'desde':item['since'],'hasta':item['through'],'sha256':h})
sources=pd.DataFrame(source_rows);sources.to_csv(OUT/'fuentes_validadas.csv',index=False)
display(sources.drop(columns='sha256'))
df,daily,extra=dataset(SOURCE)
assert not df.duplicated(KEY+['origen','horizonte']).any()
assert df.horizonte.between(1,5).all()
weekly=pd.read_parquet(SOURCE/'Datos_analiticos_proyecto/modelo_con_proyecciones_teoricas/produccion_clima_semanal.parquet')
actual=pd.read_parquet(SOURCE/'Datos_analiticos_proyecto/produccion_real_limpio.parquet',columns=['finca','semana_inicio','tallos'])
assert weekly.tallos_reales.sum()==actual.loc[actual.finca.eq('GAITANA')&actual.semana_inicio.ge('2021-01-01'),'tallos'].sum()
assert actual.tallos.notna().all() and actual.tallos.ge(0).all()
farm_audit=actual.groupby('finca').agg(registros=('tallos','size'),tallos=('tallos','sum')).reset_index()
farm_audit['en_modelo_semanal']=farm_audit.finca.eq('GAITANA')
farm_audit.to_csv(OUT/'auditoria_fincas.csv',index=False)
display(farm_audit)
other=farm_audit.loc[~farm_audit.finca.isin(['GAITANA','ARABELLA'])]
print('Etiquetas de finca fuera del alcance validado, conservadas en la fuente:',int(other.registros.sum()),'registros /',int(other.tallos.sum()),'tallos.')
print('El modelo usa GAITANA; no se reasignan etiquetas desconocidas ni se eliminan movimientos repetidos legítimos.')
engineer=engineer_archive(SOURCE,pd.read_parquet,KEY)
assert not engineer.duplicated(KEY+['origen','semana_objetivo','horizonte']).any()
closed=df.y.notna()&(df.semana_objetivo+pd.Timedelta(days=7)).le(AS_OF)
eligible=df.admisible_modelo&closed
universe=df.loc[eligible].copy()
print('Última semana objetivo cerrada con real:',universe.semana_objetivo.max().date())
''')
md('''## 2. Train, validación y test: tres funciones diferentes

* **Train de cada ajuste:** casos admisibles con objetivo observado y `semana_objetivo + 7 días <= corte`. La codificación y la imputación se ajustan sólo con esas filas.
* **Validación de selección:** noviembre–diciembre de 2025, objetivos cerrados antes del 01/01/2026. La elección Sin_clima ya fue tomada en 19; aquí se comprueba, no se vuelve a seleccionar.
* **Evaluación retrospectiva de referencia:** semanas de 2026 hasta S36. Se conserva el archivo original y se informa aparte la reconstrucción con las fuentes actuales.
* **Extensión posterior:** semanas objetivo desde S37, con semanas completas disponibles. Incluye los pronósticos de esas semanas que se habrían emitido en orígenes anteriores; se mantienen los horizontes originales. Dos protocolos sobre los mismos casos: actualización mensual del 19 y ajuste congelado al 03/08, último corte de la referencia original. El congelado no incorpora objetivos posteriores a ese corte; el mensual sólo incorpora los que ya cerraron antes de cada nuevo corte.

No hay reparto aleatorio 80/20. El porcentaje por ajuste depende de los años de historia y del tamaño del bloque futuro. **No se suman los train repetidos** para anunciar un porcentaje global. Una semana evaluada puede entrenar un ajuste posterior sin que su respuesta haya sido conocida por el ajuste que la predijo.

La extensión también es retrospectiva: septiembre fue revisado en experimentos anteriores. Octubre se informa como comprobación adicional sin tuneo en esta corrida, no como evidencia de una publicación anticipada. Ninguna de estas etiquetas certifica por sí sola que cada archivo histórico se hubiera publicado a tiempo.''')
code(r'''
common=CATEGORIES+['horizonte','semana_seno','semana_coseno']+MEMORY+WEATHER
xb=common+daily+extra
xt=common+['teoria_modelo','antiguedad_curva','desviacion_reciente_teoria']+daily+extra
excluded=WEATHER+[c for c in daily if any(v in c for v in ['temperatura','humedad','radiacion'])]
xb=[c for c in xb if c not in excluded];xt=[c for c in xt if c not in excluded]
assert 'ingeniero' not in xb+xt and 'y' not in xb+xt
assert not any(any(w in c for w in ['temperatura','humedad','radiacion']) for c in xb+xt)
pd.DataFrame([{'ruta':'Media4','variable':c} for c in xb]+[{'ruta':'Teoría','variable':c} for c in xt]).to_csv(OUT/'variables_modelo.csv',index=False)
def score(y,p):
    y=np.asarray(y,dtype=float);p=np.asarray(p,dtype=float)
    ok=np.isfinite(y)&np.isfinite(p);y=y[ok];p=p[ok];e=p-y;den=y.sum();positive=y>0
    return {'casos':len(y),'MAE':float(np.abs(e).mean()) if len(y) else None,
        'RMSE':float(np.sqrt(np.square(e).mean())) if len(y) else None,
        'WAPE':float(100*np.abs(e).sum()/den) if den else None,
        'sesgo_pct':float(100*e.sum()/den) if den else None,'sesgo_tallos':float(e.sum()),
        'MAPE_positivos':float(100*np.mean(np.abs(e[positive])/y[positive])) if positive.any() else None,
        'dentro_8_pct':float(100*np.mean(np.abs(e[positive])/y[positive]<=.08)) if positive.any() else None,
        'real_tallos':float(den),'reales_positivos':int(positive.sum())}
models={};fit_controls=[];train_scores=[]
stable_outputs={name:{k:v for k,v in item.items() if k!='sql_dataset_id'} for name,item in MANIFEST['outputs'].items()}
cache_signature=hashlib.sha256(json.dumps({'outputs':stable_outputs,'params':PARAMS,'xb':xb,'xt':xt,
    'adapter':hashlib.sha256((ROOT/'plataforma_gaitana/backend/app/model19.py').read_bytes()).hexdigest()},sort_keys=True).encode()).hexdigest()[:16]
model_folder=OUT/'modelos';model_folder.mkdir(exist_ok=True)
def train_at(cut):
    cut=pd.Timestamp(cut)
    if cut in models:return models[cut]
    tr=df.loc[df.admisible_modelo&df.y.notna()&(df.semana_objetivo+pd.Timedelta(days=7)).le(cut)].copy()
    assert len(tr) and (tr.semana_objetivo+pd.Timedelta(days=7)).le(cut).all()
    cache=model_folder/f'{cache_signature}_{cut.date()}.joblib'
    fitted=joblib.load(cache) if cache.exists() else {}
    with threadpool_limits(limits=2):
        for group,g in tr.groupby('grupo_h'):
            if group in fitted:continue
            fallback=build_model(xb).fit(g[xb],g.y-g.media_4)
            tc=g.loc[g.curva_completa]
            theory=build_model(xt).fit(tc[xt],tc.y-tc.teoria_modelo) if len(tc)>=40 else None
            fitted[group]=(fallback,theory)
    if not cache.exists():joblib.dump(fitted,cache)
    models[cut]=fitted
    fit_controls.append({'corte':cut,'train_casos':len(tr),'train_origen_desde':tr.origen.min(),
        'train_objetivo_desde':tr.semana_objetivo.min(),'train_objetivo_hasta':tr.semana_objetivo.max(),
        'train_ultimo_cierre':tr.semana_objetivo.max()+pd.Timedelta(days=7),
        'train_semanas_objetivo':tr.semana_objetivo.nunique()})
    p,_=predict(fitted,tr)
    train_scores.append({'corte':cut,'particion':'train',**score(tr.y,p)})
    if cut==max(models):
        saved=tr[KEY+['origen','semana_objetivo','horizonte','y']].copy()
        saved['prediccion']=p;saved['corte_entrenamiento']=cut
        saved.to_parquet(OUT/'predicciones_train_ultimo_ajuste.parquet',index=False)
    print('Ajustado:',cut.date(),'· train:',len(tr),flush=True)
    return fitted
def predict(fitted,te):
    p=pd.Series(index=te.index,dtype=float);route=pd.Series('memoria_4_semanas',index=te.index)
    with threadpool_limits(limits=2):
        for group,g in te.groupby('grupo_h'):
            fallback,theory=fitted[group]
            p.loc[g.index]=np.maximum(0,g.media_4+fallback.predict(g[xb]))
            tc=g.loc[g.curva_completa]
            if theory is not None and len(tc):
                p.loc[tc.index]=np.maximum(0,tc.teoria_modelo+theory.predict(tc[xt]));route.loc[tc.index]='teoria_corregida'
    assert p.notna().all() and np.isfinite(p).all()
    return p,route
def rolling(te):
    results=[]
    for month,g in te.groupby(te.origen.dt.to_period('M')):
        cut=df.loc[df.origen.dt.to_period('M').eq(month),'origen'].min()
        assert cut<=g.origen.min()
        p,route=predict(train_at(cut),g)
        z=g[KEY+['origen','semana_objetivo','horizonte','y','media_4']].copy()
        z['prediccion']=p;z['ruta']=route;z['corte_entrenamiento']=cut;results.append(z)
    return pd.concat(results,ignore_index=True)
''')
md('''## 3. Ejecución sin cambiar la selección

Se guardan los pronósticos individuales y los cortes: permiten recalcular las métricas y comprobar que ninguna semana objetivo de train termina después del corte. Los grupos y las rutas conservan exactamente la parametrización de 19. La alternativa congelada cambia únicamente la política de actualización, no la arquitectura ni los hiperparámetros.''')
code(r'''
validation_mask=universe.origen.ge('2025-11-03')&(universe.semana_objetivo+pd.Timedelta(days=7)).le(pd.Timestamp('2026-01-01'))
val=rolling(universe.loc[validation_mask])
val.to_parquet(OUT/'predicciones_validacion_2025.parquet',index=False)
test_mask=universe.origen.dt.isocalendar().year.eq(2026)&universe.semana_objetivo.dt.isocalendar().year.eq(2026)
test=rolling(universe.loc[test_mask])
test['modelo']='19_mensual_sin_clima'
extension=test.loc[test.semana_objetivo.ge(NEW_START)].copy()
assert len(extension)
frozen_input=universe.loc[test_mask&universe.semana_objetivo.ge(NEW_START)]
p,route=predict(train_at(FROZEN_CUT),frozen_input)
frozen=frozen_input[KEY+['origen','semana_objetivo','horizonte','y','media_4']].copy()
frozen['prediccion']=p;frozen['ruta']=route;frozen['corte_entrenamiento']=FROZEN_CUT;frozen['modelo']='19_congelado_03ago'
test=pd.concat([test,frozen],ignore_index=True)
assert (test.corte_entrenamiento<=test.origen).all()
test=test.merge(engineer,on=KEY+['origen','semana_objetivo','horizonte'],how='left',validate='many_to_one')
test['periodo']=np.where(test.semana_objetivo.lt(NEW_START),'referencia_hasta_S36','extension_desde_S37')
test.to_parquet(OUT/'predicciones_actualizadas.parquet',index=False)
pd.DataFrame(fit_controls).to_csv(OUT/'cortes_entrenamiento.csv',index=False)
pd.DataFrame(train_scores).to_csv(OUT/'metricas_train.csv',index=False)
display(pd.DataFrame(fit_controls))
''')
md('''## 4. Resultados comparables: modelo e ingeniero

La comparación principal exige real, predicción y estimado nominal para la misma identidad, origen, objetivo y horizonte. H1 es el inicio del nombre del archivo; no convertimos una columna de la semana en curso ni un archivo posterior en H1 nominal. Los casos sin estimado quedan contabilizados en un diagnóstico separado, no se rellenan con cero.

WAPE y sesgo se calculan a partir de los errores por caso; no se promedian porcentajes de series. MAPE y ±8 % usan sólo reales positivos. El saldo firmado siempre es predicción menos real. La comparación sigue teniendo la limitación de emisión jueves del ingeniero frente a información anterior al lunes del modelo.''')
code(r'''
rows=[]
for (period,method),g in test.groupby(['periodo','modelo']):
    paired=g.dropna(subset=['ingeniero'])
    for h,z in [('Total',paired),*[(str(int(h)),s) for h,s in paired.groupby('horizonte')]]:
        for name,col in [(method,'prediccion'),('Ingeniero','ingeniero'),('Media4','media_4')]:
            rows.append({'periodo':period,'comparacion':method,'metodo':name,'horizonte':h,
                'semanas_objetivo':z.semana_objetivo.nunique(),'origen_desde':str(z.origen.min().date()) if len(z) else '',
                'objetivo_hasta':str(z.semana_objetivo.max().date()) if len(z) else '',**score(z.y,z[col])})
metrics=pd.DataFrame(rows);metrics.to_csv(OUT/'metricas_comparadas.csv',index=False)
annual=test.loc[test.modelo.eq('19_mensual_sin_clima')].dropna(subset=['ingeniero'])
annual_rows=[]
for h,z in [('Total',annual),*[(str(int(h)),g) for h,g in annual.groupby('horizonte')]]:
    for name,column in [('19_mensual_sin_clima','prediccion'),('Ingeniero','ingeniero')]:
        annual_rows.append({'metodo':name,'horizonte':h,'semanas_objetivo':z.semana_objetivo.nunique(),**score(z.y,z[column])})
annual_metrics=pd.DataFrame(annual_rows)
annual_metrics.to_csv(OUT/'metricas_2026_completo.csv',index=False)
print('Año ISO 2026 completo: referencia y extensión, mismas parejas nominales.')
display(annual_metrics[['metodo','horizonte','casos','WAPE','sesgo_pct']])
all_scores=pd.DataFrame([{'periodo':period,'metodo':method,'horizonte':str(int(h)),**score(g.y,g.prediccion)}
    for (period,method,h),g in test.groupby(['periodo','modelo','horizonte'])])
all_scores.to_csv(OUT/'metricas_modelo_todos_los_casos.csv',index=False)
val_metrics=pd.DataFrame([{'metodo':name,**score(val.y,val[col])} for name,col in [('19_sin_clima','prediccion'),('Media4','media_4')]])
val_metrics.to_csv(OUT/'metricas_validacion_2025.csv',index=False)
display(val_metrics)
display(metrics.loc[metrics.periodo.eq('extension_desde_S37')&metrics.comparacion.eq('19_mensual_sin_clima'),
    ['metodo','horizonte','casos','semanas_objetivo','WAPE','sesgo_pct','MAE','RMSE']])
display(metrics.loc[metrics.periodo.eq('extension_desde_S37')&metrics.horizonte.eq('Total'),['comparacion','metodo','casos','WAPE','sesgo_pct']])
''')
md('''## 5. Auditoría de semanas, tamaño de prueba y ausencia de sobreajuste

Un test pequeño como porcentaje de varios años de entrenamiento no basta para diagnosticar sobreajuste. Informamos semanas y casos distintos de la evaluación acumulada, además de cada corte mensual. El error train no se compara con un test de otro ajuste. Un error de test menor tampoco demuestra ausencia de sobreajuste: puede cambiar la mezcla de productos o dificultad del período.

No ocultamos semanas faltantes: se distinguen real disponible, filas admisibles, pronósticos y pareja nominal del ingeniero. S01 de 2026 empieza el 29/12/2025 y por eso se selecciona por año ISO. El archivo original 19 se conserva, aunque esta reconstrucción pueda ampliar fechas o cambiar las identidades disponibles.''')
code(r'''
monthly=test.loc[test.modelo.eq('19_mensual_sin_clima')]
audit=[]
for dt in pd.date_range('2025-12-29',universe.semana_objetivo.max(),freq='W-MON'):
    z=monthly.loc[monthly.horizonte.eq(1)&monthly.semana_objetivo.eq(dt)]
    en=engineer.loc[engineer.finca.eq('GAITANA')&engineer.horizonte.eq(1)&engineer.semana_objetivo.eq(dt)]
    audit.append({'semana':dt.strftime('%G-S%V'),'fecha':str(dt.date()),'casos_modelo_h1':len(z),
        'casos_comparables_h1':int(z.ingeniero.notna().sum()),'estimados_nominales_h1':len(en)})
audit=pd.DataFrame(audit);audit.to_csv(OUT/'auditoria_semanas.csv',index=False)
display(audit.loc[(audit.casos_comparables_h1.eq(0))|audit.fecha.ge('2026-08-31')])
split=[]
for cut,g in monthly.groupby('corte_entrenamiento'):
    tr=next(r for r in fit_controls if r['corte']==cut)
    split.append({**tr,'test_casos':len(g),'test_origen_desde':g.origen.min(),'test_origen_hasta':g.origen.max(),
        'test_objetivo_hasta':g.semana_objetivo.max(),'test_semanas_objetivo':g.semana_objetivo.nunique(),
        'train_pct_casos':100*tr['train_casos']/(tr['train_casos']+len(g)),
        'test_pct_casos':100*len(g)/(tr['train_casos']+len(g))})
splits=pd.DataFrame(split);splits.to_csv(OUT/'particiones_por_corte.csv',index=False)
display(splits)
test_byfit=pd.DataFrame([{'corte':cut,'particion':'test',**score(g.y,g.prediccion)} for cut,g in monthly.groupby('corte_entrenamiento')])
pd.concat([pd.DataFrame(train_scores),test_byfit],ignore_index=True).to_csv(OUT/'train_test_por_ajuste.csv',index=False)
summary={'origenes_evaluados':monthly.origen.nunique(),'semanas_objetivo':monthly.semana_objetivo.nunique(),
         'casos_evaluados':len(monthly),'casos_pareados':int(monthly.ingeniero.notna().sum()),
         'objetivo_desde':str(monthly.semana_objetivo.min().date()),'objetivo_hasta':str(monthly.semana_objetivo.max().date()),
         'fecha_corrida':str(pd.Timestamp.now(tz='America/Bogota').date()),'fecha_corte_evaluacion':str(AS_OF.date()),'snapshot':MANIFEST['id'],'parametros':PARAMS,
         'sin_tuneo':True,'sin_sql_ni_vpn':True,'evaluacion_prospectiva':False}
(OUT/'resumen_ejecucion.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
display(pd.Series(summary))
''')
md('''## 6. Visualización y diagnóstico por producto

Las figuras separan el panel posterior y el panel reconstruido. Los gráficos muestran el mismo universo por método y horizonte. Este diagnóstico orienta revisiones futuras; no se usa para escoger parámetros con los propios datos de prueba.''')
code(r'''
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
recent=metrics.loc[metrics.periodo.eq('extension_desde_S37')&metrics.comparacion.eq('19_mensual_sin_clima')&metrics.horizonte.ne('Total')]
fig,axes=plt.subplots(1,2,figsize=(11,4))
for method,label,color in [('19_mensual_sin_clima','Modelo 19 · mensual','#800020'),('Ingeniero','Ingeniero','#315f82')]:
    g=recent.loc[recent.metodo.eq(method)].sort_values('horizonte')
    axes[0].plot(g.horizonte,g.WAPE,'o-',label=label,color=color)
    axes[1].plot(g.horizonte,g.sesgo_pct,'o-',label=label,color=color)
axes[0].set(ylabel='WAPE (%)',xlabel='Horizonte');axes[1].set(ylabel='Sesgo (%) · estimado − real',xlabel='Horizonte')
axes[1].axhline(0,color='gray',linewidth=.8)
for ax in axes:ax.legend(fontsize=8);ax.grid(axis='y',alpha=.18)
fig.tight_layout();fig.savefig(OUT/'figuras/extension_horizontes.png',dpi=180);plt.show()
product=[]
for (period,h,prod),g in monthly.dropna(subset=['ingeniero']).groupby(['periodo','horizonte','producto']):
    product.append({'periodo':period,'horizonte':h,'producto':prod,'casos':len(g),
        'WAPE_modelo':score(g.y,g.prediccion)['WAPE'],'WAPE_ingeniero':score(g.y,g.ingeniero)['WAPE'],
        'sesgo_modelo':score(g.y,g.prediccion)['sesgo_pct'],'sesgo_ingeniero':score(g.y,g.ingeniero)['sesgo_pct']})
products=pd.DataFrame(product);products.to_csv(OUT/'errores_producto.csv',index=False)
display(products.loc[products.periodo.eq('extension_desde_S37')&products.horizonte.eq(1)])
''')
md('''## 7. Pronóstico con la información local más reciente

Se genera una simulación del origen del lunes correspondiente al corte de evaluación (26/10), usando únicamente variables anteriores a ese origen y el ajuste mensual correspondiente. No se pronostica desde un lunes futuro con días todavía desconocidos. La fecha real de cálculo se guarda aparte de ese corte; no se presenta como pronóstico anticipado publicado el 26/10. Sus objetivos no terminados no entran en las métricas anteriores.''')
code(r'''
latest_origin=AS_OF-pd.Timedelta(days=AS_OF.dayofweek)
future=df.loc[df.origen.eq(latest_origin)&df.admisible_modelo].copy()
assert len(future)
cut=df.loc[df.origen.dt.to_period('M').eq(latest_origin.to_period('M')),'origen'].min()
p,route=predict(train_at(cut),future)
proposal=future[KEY+['origen','semana_objetivo','horizonte']].copy()
proposal['prediccion']=p;proposal['ruta']=route;proposal['fecha_calculo']=pd.Timestamp.now(tz='UTC')
proposal['estado']='simulacion_retrospectiva_no_publicada'
proposal.to_parquet(OUT/'pronostico_mas_reciente.parquet',index=False)
totals=proposal.groupby(['horizonte','semana_objetivo']).prediccion.sum().reset_index()
totals.to_csv(OUT/'totales_pronostico_reciente.csv',index=False);display(totals)
''')
md('''## 8. Qué significa reentrenar «en vivo» y qué falta validar

Aquí **no** significa aprender de cada tallo en tiempo real: es un reentrenamiento por lotes al primer origen mensual. Cargar fuentes, entrenar, evaluar y publicar son acciones distintas. Dentro del mes se reutiliza el ajuste compatible con su corte y versión de datos; una versión nueva de las fuentes puede invalidar la caché. La empresa debe acordar cuándo se congela el corte y cómo se gestionan correcciones.

Operación propuesta: (1) validar y versionar fuentes; (2) calcular variables conocidas al corte; (3) reentrenar cuando corresponde; (4) comprobar esquema, finitud, coherencia de totales y comportamiento de validación; (5) conservar la versión anterior y revisar la candidata; (6) generar y guardar la propuesta antes de observar el objetivo; (7) publicar por decisión explícita; (8) al cerrar cada objetivo, calcular WAPE y sesgo por horizonte sobre casos comparables. Registrar origen, objetivo, fecha de emisión, corte train, versión y clima. Los cambios de parámetros se validan con ventanas anteriores; no se tunea con el período final que se usa para comunicar desempeño.

Una caída de rendimiento inicia una revisión de datos, mezcla de productos, sesgo y cambios operativos; no justifica reentrenar indefinidamente hasta ganar al ingeniero. Los umbrales empresariales de alerta y promoción siguen pendientes de acuerdo. El protocolo de publicación anticipada y la comparación con igual información del jueves requieren validación operativa.

Referencias metodológicas primarias: [Hyndman y Athanasopoulos, evaluación con origen móvil](https://otexts.com/fpp3/tscv.html); [scikit-learn, prevención de fuga](https://scikit-learn.org/stable/common_pitfalls.html); [Google Cloud, validación y operación de pipelines de ML](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning). No es necesario desplegar infraestructura adicional para justificar este protocolo.''')
code(r'''
recent_table=metrics.loc[metrics.periodo.eq('extension_desde_S37')&metrics.comparacion.eq('19_mensual_sin_clima')]
m=recent_table.loc[recent_table.metodo.eq('19_mensual_sin_clima')&recent_table.horizonte.eq('Total')].iloc[0]
e=recent_table.loc[recent_table.metodo.eq('Ingeniero')&recent_table.horizonte.eq('Total')].iloc[0]
print(f"Extensión pareada: {int(m.casos):,} casos; modelo WAPE {m.WAPE:.2f} %, ingeniero {e.WAPE:.2f} %.")
print(f"Sesgo: modelo {m.sesgo_pct:.2f} %, ingeniero {e.sesgo_pct:.2f} %.")
print('El resultado se informa tal como salió; no se reajustaron parámetros para mejorar esta tabla.')
print('Las diferencias con la prueba original no son una comparación experimental pura: se ampliaron datos y semanas.')
print('Pendientes: emisión anticipada con el mismo corte del ingeniero, disponibilidad histórica de fuentes y estabilidad en más temporadas.')
assert all(r['train_ultimo_cierre']<=r['corte'] for r in fit_controls)
assert not proposal.prediccion.isna().any()
(OUT/'verificacion_final.json').write_text(json.dumps({'passed':True,'cortes_sin_objetivos_futuros':True,
    'parametros_19_conservados':True,'imputacion_solo_train':True,'ingeniero_no_predictor':True,
    'reales_ausentes_no_imputados':True,'solo_semanas_cerradas_evaluadas':True,
    'propuestas_no_publicadas':True,'resumen':summary},ensure_ascii=False,indent=2),encoding='utf-8')
''')

nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}})
path=ROOT/'Notebooks/Analisis/26_validacion_temporal_actualizada_y_operacion.ipynb'
nbf.write(nb,path);print(path)
