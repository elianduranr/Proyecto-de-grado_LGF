import hashlib
import json
from functools import lru_cache
from pathlib import Path
import numpy as np
import pandas as pd
from .config import LEGACY,STORAGE

KEY = ['finca','producto','color','variedad']
DATA = LEGACY/'Datos_analiticos_proyecto'
BASE = DATA/'modelo_con_proyecciones_teoricas'
REVIEW = DATA/'revision_clima_finca'


def runtime_root():
    from .db import Session, ActiveDataset, Dataset
    with Session() as db:
        active = db.get(ActiveDataset, 'vigente')
        if not active:return LEGACY
        root=Path(db.get(Dataset,active.dataset_id).root)
        return root if root.is_absolute() else STORAGE/root


def runtime_paths():
    root = runtime_root()
    data = root / 'Datos_analiticos_proyecto'
    return root, data, data / 'modelo_con_proyecciones_teoricas'

def records(df):
    return json.loads(df.to_json(orient='records',date_format='iso'))

@lru_cache(maxsize=8)
def _read(path, mtime):
    return pd.read_parquet(path)

def read(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'Falta la entrada del proyecto: {path.name}. Revisa LEGACY_ROOT.')
    return _read(str(path), path.stat().st_mtime_ns)

def weekly():
    return read(runtime_paths()[2]/'produccion_clima_semanal.parquet')

def comparisons():
    d=read(REVIEW/'comparacion_clima_curvas_2026.parquet')
    return d.loc[d.grupo_comparacion.eq('principal_estricta_nominal')]

def metrics(d, column):
    d=d.dropna(subset=['y',column]); denom=float(d.y.sum())
    return {'cases':len(d),'wape':float(100*(d[column]-d.y).abs().sum()/denom) if denom else None,
            'bias':float(100*(d[column]-d.y).sum()/denom) if denom else None,
            'difference':float((d[column]-d.y).sum()), 'real':denom}

def filter_frame(d, farm='', product='', color='', variety=''):
    for col,val in [('finca',farm),('producto',product),('color',color),('variedad',variety)]:
        if val: d=d.loc[d[col].eq(val)]
    return d

def options():
    d=weekly()[KEY].drop_duplicates().sort_values(KEY)
    return records(d)

def history_frame(horizon=1, farm='GAITANA', product='', color='', variety='', start='', end='', evaluation='test'):
    from .history_eval import frame, MODES
    if evaluation not in MODES: raise ValueError('Evaluación no reconocida.')
    d=filter_frame(frame(evaluation,read,REVIEW,LEGACY,runtime_root,weekly,KEY),farm,product,color,variety)
    d=d.loc[d.horizonte.eq(horizon)]
    if start: d=d.loc[d.semana_objetivo.ge(pd.Timestamp(start))]
    if end: d=d.loc[d.semana_objetivo.le(pd.Timestamp(end))]
    return d


def history(horizon=1, farm='GAITANA', product='', color='', variety='', start='', end='', evaluation='test', weeks=None):
    from .history_eval import MODES
    d=history_frame(horizon,farm,product,color,variety,start,end,evaluation)
    if weeks:
        d=d.loc[d.semana_objetivo.isin(pd.to_datetime(weeks))]
    return _history_summary(d,horizon,evaluation)


def _history_summary(d,horizon,evaluation):
    from .history_eval import MODES
    available=len(d.dropna(subset=['y','Seleccion_pre2026']))
    model_available=metrics(d,'Seleccion_pre2026')
    eligible=d.dropna(subset=['y','Seleccion_pre2026'])
    model_since=str(eligible.semana_objetivo.min().date()) if len(eligible) else None
    model_through=str(eligible.semana_objetivo.max().date()) if len(eligible) else None
    cut_note=(' Corte del ajuste: '+str(d.corte_entrenamiento.max().date())+'.') if evaluation=='train' and len(d) and 'corte_entrenamiento' in d else ''
    d=d.dropna(subset=['y','Seleccion_pre2026','ingeniero'])
    series=d.groupby('semana_objetivo')[['y','Seleccion_pre2026','ingeniero']].sum(min_count=1).reset_index()
    products=[{'product':p,'model':metrics(g,'Seleccion_pre2026'),'engineer':metrics(g,'ingeniero')} for p,g in d.groupby('producto')]
    products.sort(key=lambda g:-g['model']['real'])
    return {'model':metrics(d,'Seleccion_pre2026'),'engineer':metrics(d,'ingeniero'),
            'series':records(series),'products':products,'horizon':horizon,
            'evaluation':evaluation,'evaluation_label':MODES[evaluation][0],
            'available_cases':available,'unmatched_cases':available-len(d),'model_available':model_available,
            'model_available_since':model_since,'model_available_through':model_through,
            'scope':MODES[evaluation][0]+' · mismas series/origen/horizonte para ambos',
            'data_version':d.attrs.get('source_version'),'source_through':d.attrs.get('source_through'),
            'test_weeks':[{'date':str(pd.Timestamp(v).date()),'label':pd.Timestamp(v).strftime('%G-S%V')} for v in sorted(d.semana_objetivo.unique())],
            'origin_since':str(d.origen.min().date()) if len(d) else None,
            'origin_through':str(d.origen.max().date()) if len(d) else None,
            'evaluation_note':MODES[evaluation][1]+cut_note+' Los indicadores comparados usan únicamente casos con real, modelo e ingeniero. No se imputan estimados ausentes.'}


def error_comparison(horizon=1, farm='GAITANA', product='', color='', variety='', start='', end='', evaluation='test', level='producto', focus='model', weeks=None):
    """Error por caso antes de agregar: los errores opuestos no se compensan."""
    if level not in ['producto','color','variedad','semana_objetivo'] or focus not in ['model','engineer']:
        raise ValueError('Detalle o referencia no reconocidos.')
    if start and end and pd.Timestamp(start)>pd.Timestamp(end):
        raise ValueError('La semana inicial debe ser anterior o igual a la final.')
    universe=history_frame(horizon,farm,evaluation=evaluation)
    d=filter_frame(universe,farm,product,color,variety)
    if start:d=d.loc[d.semana_objetivo.ge(pd.Timestamp(start))]
    if end:d=d.loc[d.semana_objetivo.le(pd.Timestamp(end))]
    if weeks:d=d.loc[d.semana_objetivo.isin(pd.to_datetime(weeks))]
    summary=_history_summary(d,horizon,evaluation)
    d=d.dropna(subset=['y','Seleccion_pre2026','ingeniero']).copy()
    for name,col in [('model','Seleccion_pre2026'),('engineer','ingeniero')]:
        d[name+'_error']=d[col]-d.y
        d[name+'_absolute']=d[name+'_error'].abs()
    group={'producto':['producto'],'color':['producto','color'],'variedad':['producto','color','variedad'],
           'semana_objetivo':['semana_objetivo']}[level]
    totals={name:float(d[name+'_absolute'].sum()) for name in ['model','engineer']}
    rows=[]
    for keys,g in d.groupby(group,dropna=False):
        if not isinstance(keys,tuple):keys=(keys,)
        identity={col:(str(pd.Timestamp(value).date()) if col=='semana_objetivo' else value) for col,value in zip(group,keys)}
        row={'identity':identity,'real':float(g.y.sum()),'cases':len(g)}
        for name,col in [('model','Seleccion_pre2026'),('engineer','ingeniero')]:
            absolute=float(g[name+'_absolute'].sum())
            row[name]={**metrics(g,col),'estimate':float(g[col].sum()),'absolute':absolute,
                       'share':100*absolute/totals[name] if totals[name] else 0}
        rows.append(row)
    rows.sort(key=lambda row:-row[focus]['absolute'])
    comparable=universe.dropna(subset=['y','Seleccion_pre2026','ingeniero'])
    selectable=universe.dropna(subset=['y','Seleccion_pre2026']) if evaluation=='updated' else comparable
    weeks=sorted(pd.Timestamp(v) for v in selectable.semana_objetivo.unique())
    context=filter_frame(comparable,farm,product,color,variety)
    week_details={}
    for dt,g in context.groupby('semana_objetivo'):
        m=metrics(g,'Seleccion_pre2026');e=metrics(g,'ingeniero')
        winner=None if m['wape'] is None or e['wape'] is None else (
            'tie' if abs(m['wape']-e['wape'])<1e-9 else 'model' if m['wape']<e['wape'] else 'engineer')
        week_details[str(pd.Timestamp(dt).date())]={'winner':winner,'model_wape':m['wape'],'engineer_wape':e['wape'],'cases':len(g)}
    return {**summary,'breakdown':rows,'level':level,'focus':focus,
            'absolute_totals':totals,'identities':records(comparable[KEY].drop_duplicates().sort_values(KEY)),
            'available_weeks':[{'date':str(v.date()),'label':v.strftime('%G-S%V'),
                **week_details.get(str(v.date()),{'winner':None,'cases':0})} for v in weeks]}

def forecast_origin(frame, origin=''):
    """Sólo selecciona filas ya construidas; nunca mueve variables a otra semana."""
    default=pd.Timestamp(frame.origen.max())
    current=pd.Timestamp.now(tz='America/Bogota').tz_localize(None).normalize()
    current-=pd.Timedelta(days=current.dayofweek)
    if default>current:
        past=frame.loc[frame.origen.le(current),'origen']
        if len(past):default=pd.Timestamp(past.max())
    selected=pd.Timestamp(origin) if origin else default
    if pd.isna(selected) or selected.dayofweek != 0 or selected != selected.normalize():
        raise ValueError('H1 debe ser el lunes de una semana válida.')
    return selected,default


def status(origin=''):
    from .webflor import configured as webflor_configured
    root, current_data, current_base = runtime_paths()
    d=read(current_base/'base_analitica_proyecciones.parquet'); w=read(current_base/'produccion_clima_semanal.parquet')
    latest,default_origin=forecast_origin(d,origin)
    current=pd.Timestamp.now(tz='America/Bogota').tz_localize(None).normalize()
    current-=pd.Timedelta(days=current.dayofweek)
    available_origins=sorted(pd.Timestamp(v) for v in d.loc[d.admisible_modelo&d.origen.le(current),'origen'].unique())
    sources=[]
    from .etl import SOURCE_DIRS
    from .db import Session, ActiveDataset, Dataset, Job, Upload
    from sqlalchemy import select
    with Session() as db:
        pointer=db.get(ActiveDataset,'vigente')
        snapshot=db.get(Dataset,pointer.dataset_id) if pointer else None
        manifest=snapshot.manifest if snapshot else {}
        active_job=db.scalar(select(Job).where(Job.kind.in_(['etl','webflor']),Job.state.in_(['pendiente','en_proceso'])).order_by(Job.created_at.desc()))
        etl_job={'id':active_job.id,'progress':active_job.progress,'state':active_job.state,'message':active_job.message} if active_job else None
        receipts=db.scalars(select(Upload).where(Upload.state=='pendiente_etl')).all()
        webflor_receipts=db.scalars(select(Upload).where(Upload.source=='produccion',Upload.state=='procesado').order_by(Upload.created_at.desc()).limit(20)).all()
    for source,name,file,date in [('produccion','Producción real','produccion_real_limpio.parquet','fecha_corte'),
                           ('clima','Clima','clima_limpio.parquet','fecha'),
                           ('planos','Planos','planos_siembra_limpio.parquet','semana_inicio'),
                           ('estadisticas','Estadísticas','curvas_variedad_limpio.parquet','semana_inicio'),
                           ('estimados','Ingeniero','estimados_semanales_limpio.parquet','semana_inicio')]:
        path=current_data/file
        pending_uploads=sum(r.source==source for r in receipts)
        raw=[p for p in (LEGACY/'Datos'/SOURCE_DIRS[source]).rglob('*.xlsx') if not p.name.startswith('~$')]
        used={r['path']:r for r in manifest.get('catalog',manifest.get('sources',[])) if r['source']==source}
        pending=[p.name for p in raw if (p.relative_to(LEGACY).as_posix() not in used or
                 used[p.relative_to(LEGACY).as_posix()].get('original_mtime_ns')!=p.stat().st_mtime_ns)]
        if path.exists():
            import pyarrow.parquet as pq
            pf=pq.ParquetFile(path)
            cols=pf.schema_arrow.names
            col=date if date in cols else next((c for c in ['fecha_plano','semana_inicio','fecha'] if c in cols),None)
            extra=[c for c in ['finca','archivo_origen','origen_nominal'] if c in cols]
            dates=pd.read_parquet(path,columns=[col]+extra) if col else None
            if dates is not None and 'finca' in dates:dates=dates.loc[dates.finca.eq('GAITANA')]
            maxdate=str(dates[col].max())[:10] if dates is not None and dates[col].notna().any() else None
            latest_files=sorted({used.get(str(value).replace('\\','/'),{}).get('display_name',Path(value).name) for value in dates.loc[dates[col].eq(dates[col].max()),'archivo_origen'].dropna()})[-3:] if dates is not None and 'archivo_origen' in dates else []
            edition=str(dates.origen_nominal.max())[:10] if dates is not None and 'origen_nominal' in dates and dates.origen_nominal.notna().any() else None
            sources.append({'name':name,'source':source,'rows':pf.metadata.num_rows,'through':maxdate,
                            'state':'procesado' if snapshot else 'parquet_anterior', 'raw_files':len(raw),
                            'pending_files':len(pending),'pending_uploads':pending_uploads,'examples':pending[-3:],
                            'action':'Procesar archivos disponibles' if pending or pending_uploads else 'Fuente procesada; puede cargar una actualización',
                            'required':source in ['produccion','planos','estadisticas'],
                            'loaded_files':sum(r.get('active',True) for r in used.values()),'latest_files':latest_files,'latest_edition':edition})
            if dates is not None:
                check='origen_nominal' if source=='estimados' else col
                sources[-1]['reference_available']=bool(pd.to_datetime(dates[check]).eq(latest).any()) if check else False
        else: sources.append({'name':name,'source':source,'rows':0,'through':None,'state':'pendiente',
                              'raw_files':len(raw),'pending_files':len(pending),'pending_uploads':pending_uploads,'examples':pending[-3:],
                              'action':'Procesar archivos disponibles' if raw else 'Cargar archivo de esta fuente','required':source in ['produccion','planos','estadisticas']})
    prior=comparisons()
    bias=[{'horizon':int(h),'model':metrics(g,'Seleccion_pre2026'),'engineer':metrics(g,'ingeniero')} for h,g in prior.groupby('horizonte')]
    validation=read(REVIEW/'validacion_clima_pre2026.parquet')
    validation_bias={v:[{'horizon':int(h),**metrics(g,v)} for h,g in validation.groupby('horizonte')] for v in ['Sin_clima','Clima_basico']}
    required=[current_base/'base_analitica_proyecciones.parquet',current_base/'produccion_clima_semanal.parquet',
              current_data/'modelo_diario/features_diarias.parquet',root/'Notebooks/Analisis/19_modelos_clima_y_curvas_gaitana.ipynb']
    latest_cases=d.loc[d.origen.eq(latest)&d.admisible_modelo]
    basis={'cases':len(latest_cases),'theory':int(latest_cases.curva_completa.sum()),
           'memory':int((~latest_cases.curva_completa).sum()),
           'missing_plan':int(latest_cases.fecha_plano.isna().sum())}
    for source in sources:
        through=pd.Timestamp(source['through']) if source['through'] else None
        pending=bool(source['pending_files'] or source['pending_uploads'])
        source['status_label']='Por procesar' if pending else ('Sin fuente' if through is None else 'Procesado')
        source['tone']='amber' if pending or through is None else 'green'
        source['next_from']=str((through+pd.Timedelta(days=1)).date()) if through is not None else None
        source['period_needed']=None
        source['purpose']=''
        if source['source']=='produccion':
            source['period_needed']=f"Cortes anteriores a H1 ({latest.date()})"
            source['purpose']='Necesaria para los rezagos y tendencias. WebFlor reconsulta hasta ayer y sustituye la ventana reciente, incluidas correcciones de días ya cargados.'
            source['instruction']=f"Actualizar desde WebFlor; si usa Excel adicional, fechas desde {source['next_from']}." if through is not None else 'Cargue el histórico completo antes de actualizar por WebFlor.'
            current_hashes={r['sha256'] for r in manifest.get('catalog',[]) if r.get('active',True) and r['source']=='produccion'}
            receipt=next((r for r in webflor_receipts if r.sha256 in current_hashes and r.report.get('source')=='WebFlor'),None)
            if receipt:source['webflor_closed_through']=receipt.report.get('closed_through')
            closed_windows=[r['replace_window']['end'] for r in manifest.get('catalog',[]) if r['source']=='produccion' and r.get('active',True) and r.get('replace_window')]
            if closed_windows:source['webflor_closed_through']=max(closed_windows+[source.get('webflor_closed_through') or ''])
        elif source['source']=='planos':
            source['period_needed']=f"Plano {latest.strftime('%G-S%V')} para la teoría de H1"
            source['purpose']='Su actualización permite usar las proyecciones teóricas; si no hay plano de este origen, el modelo usa producción reciente.'
            next_week=(through+pd.Timedelta(days=7)).strftime('%G-S%V') if through is not None else latest.strftime('%G-S%V')
            source['instruction']=f"Suba los planos faltantes desde {next_week}; no reenvíe semanas ya cargadas."
            if not source.get('reference_available') and not pending:source['status_label']='Actualizar para teoría';source['tone']='amber'
            if source.get('reference_available'):
                source['instruction']=f"El plano de {latest.strftime('%G-S%V')} ya está procesado. Suba sólo planos nuevos."
        elif source['source']=='clima':
            source['period_needed']=f"Semana previa a H1: {(latest-pd.Timedelta(days=7)).strftime('%G-S%V')}"
            source['purpose']='Opcional. Sin clima sigue funcionando con producción reciente y la teoría aplicable.'
            source['instruction']=f"Adicional: desde {source['next_from']}; o archivo completo del año." if through is not None else 'Suba un archivo completo si desea utilizar la variante climática.'
            if (through is None or through<latest-pd.Timedelta(days=7)) and not pending:source['status_label']='Opcional · sin clima';source['tone']='amber'
        elif source['source']=='estadisticas':
            source['period_needed']='No requiere una edición cada semana'
            source['purpose']='Las curvas históricas siguen siendo utilizables. Se recomienda actualizar cuando existan nuevas observaciones.'
            source['instruction']='Suba el archivo completo actualizado del año y familia; no sólo las filas nuevas.'
        else:
            source['period_needed']=f"Edición cuyo H1 es {latest.strftime('%G-S%V')}"
            source['purpose']='Opcional; sirve para comparar desempeño. Nunca se utiliza para predecir.'
            source['instruction']='Suba las nuevas ediciones; el inicio del nombre identifica H1 y se conservan las anteriores.'
            if not pending and not source.get('reference_available'):
                source['status_label']='Falta edición · opcional';source['tone']='amber'
        if not source['pending_files'] and not source['pending_uploads']:
            if source['source']=='planos' and basis['missing_plan']:
                source['action']=f"Para incorporar la teoría del origen, cargue el plano de {latest.strftime('%G-S%V')}. La ruta de producción reciente sigue disponible."
            elif source['source']=='clima' and (not source['through'] or pd.Timestamp(source['through'])<latest-pd.Timedelta(days=7)):
                source['action']=f"Para habilitar clima, actualice al menos hasta la semana de {(latest-pd.Timedelta(days=7)).date()}. Sin clima sigue disponible."
    has_cases=bool(len(latest_cases)) and latest<=current
    return {'origin':str(latest.date()),'default_origin':str(default_origin.date()),
            'available_origins':[str(v.date()) for v in available_origins],
            'generation_note':('Semana disponible en la base procesada. Si elige un origen pasado, se genera una simulación retrospectiva, no una nueva prueba independiente.' if has_cases else
                f"La semana anterior a H1 {latest.strftime('%G-S%V')} todavía no ha terminado. No se usan días futuros ni un corte parcial para preparar ese origen." if latest>current else
                f"No hay variables procesadas para H1 {latest.strftime('%G-S%V')}. Actualice la producción real anterior a ese lunes y procese los archivos. El último origen preparado es {default_origin.strftime('%G-S%V')}."),
            'latest_observed_week':str(w.semana_inicio.max().date()),
            'data_age_days':int((pd.Timestamp.now().normalize()-latest).days),
            'ready':has_cases and all(p.exists() for p in required)
                    and not any(s['pending_files'] or s['pending_uploads'] for s in sources if s['required']) and not etl_job,
            'sources':sources,'horizons':bias,'validation_bias':validation_bias,'farms_validated':['GAITANA'],'prediction_basis':basis,
            'dataset_id':snapshot.id if snapshot else None,'etl_job':etl_job,'webflor_configured':webflor_configured(),
            'processing_required':any(s['pending_files'] or s['pending_uploads'] for s in sources),
            'climate_ready':next((s['through'] is not None and pd.Timestamp(s['through'])>=latest-pd.Timedelta(days=7) for s in sources if s['source']=='clima'),False),
            'variants':[{'id':'Sin_clima','label':'Boosting sin clima · recomendado'},
                        {'id':'Clima_basico','label':'Clima básico · variante experimental del 19'}],
            'notice':'El origen usa los datos limpios de la última carga validada. Clima e ingeniero no son obligatorios para la variante Sin clima. Los archivos originales pendientes deben procesarse antes de avanzar el corte.'}

def curve(product, variety, color='', origin=''):
    # Preferir las curvas usadas por proyecciones; nunca normalizar por máximos.
    root=runtime_root()/'Notebooks/Proyecciones Teoricas Propias/resultados_todos_los_anios'
    files=[p for p in root.rglob('*.parquet') if 'curva' in p.name.lower() and 'cobertura' not in p.name.lower()]
    for p in sorted(files,reverse=True):
        import pyarrow.parquet as pq
        cols=pq.ParquetFile(p).schema_arrow.names
        age=next((c for c in ['edad_semanas','edad','Edad'] if c in cols),None)
        value=next((c for c in ['rendimiento_curva','flores_por_planta','rendimiento','rendimiento_medio','productividad'] if c in cols),None)
        if not age or not value: continue
        d=read(p)
        if 'clave_curva' in d:
            parts=d.clave_curva.str.split('|',expand=True)
            if parts.shape[1]<4:continue
            mask=parts[1].eq(product.upper()) & parts[3].eq(variety.upper())
            if color:mask &=parts[2].eq(color.upper())
            d=d.loc[mask]
        elif 'variedad' in d:
            d=d.loc[d.variedad.astype(str).str.upper().eq(variety.upper())]
            if 'producto' in d: d=d.loc[d.producto.astype(str).str.upper().eq(product.upper())]
        else: continue
        if 'fecha_plano' in d:
            if origin:d=d.loc[d.fecha_plano.le(pd.Timestamp(origin))]
            if len(d):d=d.loc[d.fecha_plano.eq(d.fecha_plano.max())]
        if len(d) and 'clave_curva' in d and d.clave_curva.nunique()>1:
            return {'series':[],'unit':'tallos por planta / semana','note':'Selecciona un color para distinguir las curvas de esta variedad. No se promedian identidades distintas.'}
        if len(d):
            if 'plano' in d: d=d.loc[d.plano.eq(d.plano.max())]
            g=d.groupby(age)[value].mean().reset_index().rename(columns={age:'age',value:'yield'})
            return {'series':records(g),'unit':'tallos por planta / semana','source':str(p.relative_to(root)),
                    'note':'Curva normalizada por planta. Se muestra aparte del pronóstico absoluto.'}
    return {'series':[],'unit':'tallos por planta / semana','note':'No se encontró una curva final identificable para esta selección. No se reconstruye una curva distinta de la validada.'}

def snapshot_hash(root=None):
    if root is None:
        _, current_data, current_base = runtime_paths()
    else:
        current_data=Path(root)/'Datos_analiticos_proyecto';current_base=current_data/'modelo_con_proyecciones_teoricas'
    reference_root=Path(root) if root else runtime_paths()[0]
    paths=[current_base/'base_analitica_proyecciones.parquet',current_base/'produccion_clima_semanal.parquet',
           current_data/'modelo_diario/features_diarias.parquet',reference_root/'Notebooks/Analisis/19_modelos_clima_y_curvas_gaitana.ipynb']
    h=hashlib.sha256()
    for p in paths:
        with p.open('rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
