"""Adaptador de la variante del 19. Sin tuning ni uso del ingeniero como entrada."""
import ast
import hashlib
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from threadpoolctl import threadpool_limits
from .config import LEGACY, STORAGE
from .data import KEY, read, snapshot_hash, runtime_paths

CATEGORIES=['producto','color','variedad']
MEMORY=['produccion_lag1','produccion_lag2','produccion_lag3','media_4','media_8','desv_4','tendencia_4_8','cambio_reciente','produccion_52']
WEATHER=[v+s for v in ['temperatura_semana','humedad_semana','radiacion_semana'] for s in ['_lag1','_media4']]
PARAMS=dict(learning_rate=.08,max_iter=80,max_leaf_nodes=15,min_samples_leaf=40,l2_regularization=1.0,early_stopping=False,random_state=42)

def build_model(columns):
    prepare=ColumnTransformer([
        ('categorias',OneHotEncoder(handle_unknown='ignore',sparse_output=False,dtype=np.float32),CATEGORIES),
        ('numericas',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True),[c for c in columns if c not in CATEGORIES])])
    return make_pipeline(prepare,HistGradientBoostingRegressor(**PARAMS))

def memory_function(root=None):
    """Reutiliza la función exacta del notebook; no ejecuta sus celdas de evaluación."""
    path=Path(root or LEGACY)/'Notebooks/Analisis/19_modelos_clima_y_curvas_gaitana.ipynb'
    notebook=json.loads(path.read_text(encoding='utf-8'))
    code='\n'.join(''.join(c['source']) for c in notebook['cells'] if c['cell_type']=='code')
    node=next(n for n in ast.parse(code).body if isinstance(n,ast.FunctionDef) and n.name=='memoria_larga')
    ns={'pd':pd,'KEY':KEY}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),ns)
    return ns['memoria_larga']

def dataset(root=None):
    if root is None:
        root, DATA, BASE = runtime_paths()
    else:
        DATA=Path(root)/'Datos_analiticos_proyecto';BASE=DATA/'modelo_con_proyecciones_teoricas'
    df=read(BASE/'base_analitica_proyecciones.parquet').copy()
    f=read(DATA/'modelo_diario/features_diarias.parquet')
    daily=[c for c in f if c not in KEY+['fecha']]
    df=df.merge(f.rename(columns={'fecha':'origen'}),on=KEY+['origen'],how='left',validate='many_to_one')
    extra=memory_function(root)(read(BASE/'produccion_clima_semanal.parquet'))
    extra_cols=[c for c in extra if c not in KEY+['origen']]
    df=df.merge(extra,on=KEY+['origen'],how='left',validate='many_to_one')
    df['tendencia_4_12']=df.media_4-df.media_12
    extra_cols+=['tendencia_4_12']
    df['grupo_h']=np.where(df.horizonte.le(2),'H1_H2','H3_H5')
    return df,daily,extra_cols

def run_forecast(origin, variant, progress=lambda value,message:None, source_root=None):
    if variant not in ('Sin_clima','Clima_basico'):
        raise ValueError('Variante no habilitada para el prototipo.')
    progress(5,'Leyendo las entradas y verificando su versión')
    source_root=Path(source_root) if source_root else runtime_paths()[0]
    version=snapshot_hash(source_root)
    adapter_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    df,daily,extra=dataset(source_root)
    origin=pd.Timestamp(origin)
    test=df.loc[df.origen.eq(origin)&df.admisible_modelo].copy()
    if test.empty: raise ValueError('Este origen no tiene filas admisibles en la base procesada.')
    # Mismo primer origen mensual que el protocolo retrospectivo del 19.
    month=df.loc[df.origen.dt.to_period('M').eq(origin.to_period('M')),'origen'].min()
    train=df.loc[df.y.notna()&df.admisible_modelo&(df.semana_objetivo+pd.Timedelta(days=7)).le(month)].copy()
    assert (train.semana_objetivo+pd.Timedelta(days=7)).le(month).all()
    common=CATEGORIES+['horizonte','semana_seno','semana_coseno']+MEMORY+WEATHER
    xb=common+daily+extra
    xt=common+['teoria_modelo','antiguedad_curva','desviacion_reciente_teoria']+daily+extra
    if variant=='Sin_clima':
        excluded=WEATHER+[c for c in daily if any(v in c for v in ['temperatura','humedad','radiacion'])]
        xb=[c for c in xb if c not in excluded]
        xt=[c for c in xt if c not in excluded]
    cache=STORAGE/'models'/f'{version}_{adapter_hash[:12]}_{variant}_{month.date()}.joblib'
    cache.parent.mkdir(parents=True,exist_ok=True)
    models=joblib.load(cache) if cache.exists() else {}
    prediction=pd.Series(index=test.index,dtype=float)
    route=pd.Series('memoria_4_semanas',index=test.index)
    for i,(group,te) in enumerate(test.groupby('grupo_h')):
        tr=train.loc[train.grupo_h.eq(group)]
        if tr.empty: raise ValueError(f'No hay entrenamiento para {group}.')
        progress(15+i*35,f'Ajustando {group}: producción reciente y teoría cuando aplica')
        with threadpool_limits(limits=2):
            if group not in models:
                fallback=build_model(xb).fit(tr[xb],tr.y-tr.media_4)
                tc=tr.loc[tr.curva_completa]
                theory=build_model(xt).fit(tc[xt],tc.y-tc.teoria_modelo) if len(tc)>=40 else None
                models[group]=(fallback,theory)
            fallback,theory=models[group]
            prediction.loc[te.index]=np.maximum(0,te.media_4+fallback.predict(te[xb]))
            ec=te.loc[te.curva_completa]
            if theory is not None and len(ec):
                prediction.loc[ec.index]=np.maximum(0,ec.teoria_modelo+theory.predict(ec[xt]))
                route.loc[ec.index]='teoria_corregida'
    if not cache.exists():
        temporary=cache.with_suffix('.tmp');joblib.dump(models,temporary);temporary.replace(cache)
    assert prediction.notna().all() and np.isfinite(prediction).all()
    test['prediction']=prediction;test['route']=route
    result=test[KEY+['origen','semana_objetivo','horizonte','prediction','route','teoria_modelo']].copy()
    metadata={'reference':'Cuadernillo 19','variant':variant,'data_hash':version,'dataset_id':source_root.name if source_root.parent.name=='datasets' else 'referencia_notebooks','adapter_version':'0.1.0','adapter_sha256':adapter_hash,'training_cutoff':str(month.date()),
              'training_cases':len(train),'parameters':PARAMS,'columns_fallback':xb,'columns_theory':xt,
              'status':'adaptador_en_verificacion','note':'Inferencia real del adaptador. No se declara equivalencia completa hasta finalizar la regresión histórica.'}
    return result,metadata
