import io
import logging
import math
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Literal
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from .config import DEV_MODE, DATABASE_URL, CORS
from .db import Session, Forecast, Job, Line, Audit, Publication, Upload, now
from .security import identity, can_edit
from .adjustments import allocate
from . import data
from .uploads import receive

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s %(message)s')
log=logging.getLogger('gaitana')
app=FastAPI(title='La Gaitana · Producción',version='0.1.0',description='Prototipo con fuentes reales. Referencia: cuadernillo 19.')
app.add_middleware(CORSMiddleware,allow_origins=CORS,allow_methods=['GET','POST'],allow_headers=['Authorization','Content-Type'])

def db_session():
    with Session() as db: yield db

@app.exception_handler(FileNotFoundError)
async def missing(request, exc):
    return JSONResponse(status_code=503,content={'detail':str(exc)})

@app.exception_handler(ValueError)
async def invalid(request,exc):
    return JSONResponse(status_code=422,content={'detail':str(exc)})

@app.exception_handler(Exception)
async def internal(request,exc):
    log.exception('Fallo en %s',request.url.path)
    return JSONResponse(status_code=500,content={'detail':'No se pudo completar la operación. Revisa el registro del backend.'})

@app.get('/api/health')
def health():
    return {'status':'ok','version':'0.1.0'}

@app.get('/api/session')
def session(role=Depends(identity)):
    return {'role':role,'development':DEV_MODE,'database':'SQLite local' if DATABASE_URL.startswith('sqlite') else 'SQL Server',
            'prototype':True,'notice':'Prototipo local: autenticación por token. Configurar identidad corporativa antes de desplegar públicamente.'}

@app.get('/api/data/status')
def status(origin:str=Query('',pattern=r'^(\d{4}-\d{2}-\d{2})?$'),role=Depends(identity)):
    return data.status(origin)

@app.get('/api/options')
def options(role=Depends(identity)):
    return data.options()

@app.get('/api/history')
def history(horizon:int=Query(1,ge=1,le=5),farm='GAITANA',product='',color='',variety='',start='',end='',evaluation:Literal['train','validation','test','live','updated']='test',role=Depends(identity)):
    return data.history(horizon,farm,product,color,variety,start,end,evaluation)

@app.get('/api/comparison')
def comparison(horizon:int=Query(1,ge=1,le=5),farm='GAITANA',product='',color='',variety='',start='',end='',
               evaluation:Literal['train','validation','test','live','updated']='test',
               level:Literal['producto','color','variedad','semana_objetivo']='producto',
               focus:Literal['model','engineer']='model',weeks:str='',role=Depends(identity)):
    selected=weeks.split(',') if weeks else None
    if selected and len(selected)>530:raise HTTPException(422,'Seleccione como máximo 530 semanas.')
    return data.error_comparison(horizon,farm,product,color,variety,start,end,evaluation,level,focus,selected)


@app.get('/api/forecasts/{forecast_id}/performance')
def forecast_performance(forecast_id:str,role=Depends(identity),db=Depends(db_session)):
    row=db.get(Forecast,forecast_id)
    if not row:raise HTTPException(404,'Pronóstico no encontrado.')
    lines=db.scalars(select(Line).where(Line.forecast_id==forecast_id)).all()
    d=pd.DataFrame([{'finca':row.farm,'producto':r.product,'color':r.color,'variedad':r.variety,
        'semana_objetivo':pd.Timestamp(r.target),'horizonte':r.horizon,
        'model':r.model_value,'adjusted':r.final_value} for r in lines])
    w=data.weekly().rename(columns={'semana_inicio':'semana_objetivo','tallos_reales':'y'})
    if len(d):
        d=d.merge(w[data.KEY+['semana_objetivo','y']],on=data.KEY+['semana_objetivo'],how='inner',validate='many_to_one')
        now=pd.Timestamp.now(tz='America/Bogota').tz_localize(None).normalize()
        through=pd.Timestamp(pd.read_parquet(data.runtime_paths()[1]/'produccion_real_limpio.parquet',columns=['fecha_corte']).fecha_corte.max())
        d=d.loc[(d.semana_objetivo+pd.Timedelta(days=7)).le(now)&(d.semana_objetivo+pd.Timedelta(days=6)).le(through)]
    if not len(d):d=pd.DataFrame(columns=['y','model','adjusted'])
    return {'forecast_id':row.id,'revision':row.revision,'model':data.metrics(d,'model'),
        'adjusted':data.metrics(d,'adjusted'),'note':'Sólo semanas terminadas y cubiertas por la producción cargada. El ajuste manual se evalúa aparte de la sugerencia original; modificarlo no crea una predicción anticipada.'}


@app.get('/api/series')
def series(farm='GAITANA',product='',color='',variety='',start='',end='',forecast_id='',detail:bool=False,role=Depends(identity),db=Depends(db_session)):
    d=data.filter_frame(data.weekly(),farm,product,color,variety)
    if forecast_id:
        run=db.get(Forecast,forecast_id)
        if not run:raise HTTPException(404,'Pronóstico no encontrado.')
        keys=db.execute(select(Line.product,Line.color,Line.variety).where(Line.forecast_id==run.id).distinct()).all()
        scope=pd.DataFrame(keys,columns=['producto','color','variedad'])
        d=d.loc[d.finca.eq(run.farm)].merge(scope,on=['producto','color','variedad'],how='inner',validate='many_to_one')
    if start:d=d.loc[d.semana_inicio.ge(pd.Timestamp(start))]
    if end:d=d.loc[d.semana_inicio.le(pd.Timestamp(end))]
    groups=['producto','color','variedad','semana_inicio'] if detail else ['semana_inicio']
    return data.records(d.groupby(groups).tallos_reales.sum(min_count=1).reset_index())

@app.get('/api/curve')
def curve(product:str,variety:str,color='',origin='',role=Depends(identity)):
    return data.curve(product,variety,color,origin)

class Generate(BaseModel):
    origin:str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    variant:Literal['Sin_clima','Clima_basico']='Sin_clima'

@app.post('/api/forecasts',status_code=202)
def generate(body:Generate,role=Depends(identity),db=Depends(db_session)):
    can_edit(role)
    datetime.strptime(body.origin,'%Y-%m-%d')
    state=data.status(body.origin)
    if not state['ready']:
        raise HTTPException(422,state['generation_note']+' Revisa también las fuentes obligatorias pendientes de procesar.')
    if body.variant=='Clima_basico' and not state['climate_ready']:
        raise HTTPException(422,'No hay clima reciente para este origen. Actualiza Clima o selecciona el modelo Sin clima.')
    source=data.read(data.runtime_paths()[2]/'base_analitica_proyecciones.parquet')
    if not source.loc[source.origen.eq(pd.Timestamp(body.origin))&source.admisible_modelo].shape[0]:
        raise HTTPException(422,'El origen no tiene variables procesadas admisibles. Actualiza primero la base analítica.')
    pending=db.scalar(select(Job).where(Job.state.in_(['pendiente','en_proceso'])))
    if pending: raise HTTPException(409,'Ya hay una generación en proceso. Espera a que termine.')
    job=Job(kind='forecast',payload={**body.model_dump(),'actor':role})
    db.add(job);db.flush();db.add(Audit(actor=role,action='generacion_solicitada',object_id=job.id,details=body.model_dump()));db.commit()
    return {'job_id':job.id}


@app.post('/api/data/rebuild',status_code=202)
def rebuild_sources(role=Depends(identity),db=Depends(db_session)):
    can_edit(role)
    if db.scalar(select(Job).where(Job.state.in_(['pendiente','en_proceso']))):
        raise HTTPException(409,'Hay un ETL o pronóstico en proceso; espera a que termine.')
    job=Job(kind='etl',payload={'actor':role})
    db.add(job);db.flush()
    db.add(Audit(actor=role,action='etl_solicitado',object_id=job.id,details={'sources':'archivos disponibles y cargas recibidas'}))
    db.commit()
    return {'job_id':job.id}

@app.get('/api/jobs/{job_id}')
def get_job(job_id:str,role=Depends(identity),db=Depends(db_session)):
    row=db.get(Job,job_id)
    if not row:raise HTTPException(404,'Trabajo no encontrado.')
    return {'id':row.id,'state':row.state,'progress':row.progress,'message':row.message,'result':row.result}


@app.post('/api/data/webflor',status_code=202)
def update_webflor(role=Depends(identity),db=Depends(db_session)):
    can_edit(role)
    from .webflor import configured
    from .db import ActiveDataset
    if not configured():raise HTTPException(422,'WebFlor no está configurado en este servidor.')
    if not db.get(ActiveDataset,'vigente'):raise HTTPException(422,'Primero debe terminar la carga inicial de fuentes.')
    if db.scalar(select(Job).where(Job.state.in_(['pendiente','en_proceso']))):
        raise HTTPException(409,'Hay un procesamiento en curso; espera a que termine.')
    if db.scalar(select(Upload).where(Upload.state=='pendiente_etl',Upload.source=='produccion',Upload.mode=='completo')):
        raise HTTPException(409,'Procese primero el archivo completo de producción pendiente. Después podrá actualizar su ventana reciente desde WebFlor.')
    job=Job(kind='webflor',payload={'actor':role})
    db.add(job);db.flush();db.add(Audit(actor=role,action='webflor_solicitado',object_id=job.id,details={'source':'Reporte.InformeCorteInvVariedad','mode':'reconsulta y reemplazo versionado de últimos 45 días hasta ayer'}));db.commit()
    return {'job_id':job.id}

def summary(row):
    return {'id':row.id,'origin':row.origin,'farm':row.farm,'variant':row.variant,'state':row.state,
            'revision':row.revision,'created_at':row.created_at.isoformat(),'metadata':row.metadata_json}

@app.get('/api/forecasts')
def forecasts(role=Depends(identity),db=Depends(db_session)):
    return [summary(r) for r in db.scalars(select(Forecast).order_by(Forecast.created_at.desc()).limit(100))]

@app.get('/api/forecasts/{forecast_id}')
def forecast(forecast_id:str,role=Depends(identity),db=Depends(db_session)):
    row=db.get(Forecast,forecast_id)
    if not row:raise HTTPException(404,'Pronóstico no encontrado.')
    lines=db.scalars(select(Line).where(Line.forecast_id==row.id).order_by(Line.product,Line.color,Line.variety,Line.horizon)).all()
    return {**summary(row),'lines':[{'id':r.id,'product':r.product,'color':r.color,'variety':r.variety,'horizon':r.horizon,
            'target':r.target,'model':r.model_value,'final':r.final_value,'theory':r.theory,'route':r.route} for r in lines]}

class Adjustment(BaseModel):
    expected_revision:int=Field(ge=0)
    horizon:int=Field(ge=1,le=5)
    product:str
    color:str=''
    variety:str=''
    total:int=Field(ge=0,le=1_000_000_000)
    note:str=Field(default='',max_length=1000)
    restore:bool=False

def lock_draft(db,id,revision):
    row=db.get(Forecast,id)
    if not row:raise HTTPException(404,'Pronóstico no encontrado.')
    changed=db.execute(update(Forecast).where(Forecast.id==id,Forecast.revision==revision,Forecast.state=='borrador').values(revision=revision+1))
    if changed.rowcount!=1:
        db.rollback();raise HTTPException(409,'La versión cambió o está publicada. Recarga el borrador; las publicaciones no se editan.')
    return row


@app.get('/api/forecasts/{forecast_id}/reviews')
def reviews(forecast_id:str,role=Depends(identity),db=Depends(db_session)):
    from .reviews import review_summary
    run=db.get(Forecast,forecast_id)
    if not run:raise HTTPException(404,'Pronóstico no encontrado.')
    lines=db.scalars(select(Line).where(Line.forecast_id==forecast_id)).all()
    return {'revision':run.revision,**review_summary(lines,run.metadata_json.get('reviews',{}))}


class ReviewIdentity(BaseModel):
    product:str=Field(min_length=1,max_length=150)
    color:str=Field(min_length=1,max_length=150)
    variety:str=Field(min_length=1,max_length=150)


class ReviewAction(BaseModel):
    expected_revision:int=Field(ge=0)
    identities:list[ReviewIdentity]=Field(min_length=1,max_length=500)
    action:Literal['reviewed','pending']='reviewed'


@app.post('/api/forecasts/{forecast_id}/reviews')
def save_reviews(forecast_id:str,body:ReviewAction,role=Depends(identity),db=Depends(db_session)):
    from .reviews import identity_key,fingerprint,review_summary
    can_edit(role);run=lock_draft(db,forecast_id,body.expected_revision)
    lines=db.scalars(select(Line).where(Line.forecast_id==forecast_id)).all()
    saved=dict(run.metadata_json.get('reviews',{}));changes=[]
    for item in body.identities:
        group=[r for r in lines if (r.product,r.color,r.variety)==(item.product,item.color,item.variety)]
        if not group:raise HTTPException(422,'La variedad seleccionada no pertenece a esta propuesta.')
        key=identity_key(item.product,item.color,item.variety)
        if body.action=='pending':saved.pop(key,None);status='pendiente'
        else:
            status='ajustada' if any(r.final_value!=int(math.floor(r.model_value+.5)) for r in group) else 'aceptada'
            saved[key]={'status':status,'at':now().isoformat(),'actor':role,'fingerprint':fingerprint(group)}
        changes.append({**item.model_dump(),'status':status})
    run.metadata_json={**run.metadata_json,'reviews':saved}
    db.add(Audit(actor=role,action='revision_variedades',object_id=run.id,details={'changes':changes,'revision':body.expected_revision+1}))
    db.commit()
    return {'revision':body.expected_revision+1,**review_summary(lines,saved)}

@app.post('/api/forecasts/{forecast_id}/adjustments')
def adjust(forecast_id:str,body:Adjustment,role=Depends(identity),db=Depends(db_session)):
    can_edit(role);run=lock_draft(db,forecast_id,body.expected_revision)
    query=select(Line).where(Line.forecast_id==forecast_id,Line.horizon==body.horizon,Line.product==body.product)
    if body.color:query=query.where(Line.color==body.color)
    if body.variety:query=query.where(Line.variety==body.variety)
    rows=db.scalars(query.order_by(Line.color,Line.variety,Line.id)).all()
    if not rows:raise HTTPException(422,'No hay filas en esta selección.')
    values=[int(math.floor(r.model_value+.5)) for r in rows] if body.restore else allocate(body.total,[r.final_value for r in rows])
    differences=[]
    for row,value in zip(rows,values):
        differences.append({'line_id':row.id,'previous':row.final_value,'value':value});row.final_value=value
    from .reviews import identity_key
    saved=dict(run.metadata_json.get('reviews',{}))
    for row,change in zip(rows,differences):
        if change['previous']!=change['value']:saved.pop(identity_key(row.product,row.color,row.variety),None)
    run.metadata_json={**run.metadata_json,'reviews':saved}
    db.add(Audit(actor=role,action='restaurar' if body.restore else 'ajustar',object_id=forecast_id,
                 details={'revision':body.expected_revision+1,'note':body.note,'changes':differences}))
    db.commit();return {'revision':body.expected_revision+1,'total':sum(values)}

class Publish(BaseModel):
    expected_revision:int=Field(ge=0)

@app.post('/api/forecasts/{forecast_id}/publish')
def publish(forecast_id:str,body:Publish,role=Depends(identity),db=Depends(db_session)):
    can_edit(role);row=lock_draft(db,forecast_id,body.expected_revision)
    current=db.scalar(select(Publication).where(Publication.farm==row.farm,Publication.origin==row.origin))
    if current:
        previous=db.get(Forecast,current.forecast_id);previous.state='reemplazado'
        current.forecast_id=row.id;current.revision=body.expected_revision+1;current.published_at=now()
    else:db.add(Publication(farm=row.farm,origin=row.origin,forecast_id=row.id,revision=body.expected_revision+1))
    row.state='publicado'
    db.add(Audit(actor=role,action='publicar',object_id=row.id,details={'revision':body.expected_revision+1}))
    try:db.commit()
    except IntegrityError:
        db.rollback();raise HTTPException(409,'Se publicó otra versión al mismo tiempo. Recarga para revisar la vigente.')
    return {'state':'publicado','revision':body.expected_revision+1}

@app.get('/api/forecasts/{forecast_id}/export')
def export(forecast_id:str,role=Depends(identity),db=Depends(db_session)):
    body=forecast(forecast_id,role,db)
    d=pd.DataFrame(body['lines'])
    if d.empty:raise HTTPException(422,'No hay líneas para exportar.')
    detail=d.rename(columns={'product':'Producto','color':'Color','variety':'Variedad','target':'Semana','final':'Estimado ajustado','model':'Sugerencia modelo'})
    wide=detail.pivot_table(index=['Producto','Color','Variedad'],columns='Semana',values='Estimado ajustado',aggfunc='sum')
    buffer=io.BytesIO()
    with pd.ExcelWriter(buffer,engine='openpyxl') as writer:
        wide.to_excel(writer,sheet_name='Estimado')
        detail.to_excel(writer,sheet_name='Trazabilidad',index=False)
        pd.DataFrame([{'Origen':body['origin'],'Modelo':body['variant'],'Version':body['id'],'Estado':body['state'],
                       'Nota':'Exportación del prototipo. No replica aún la plantilla dinámica oficial del ingeniero.'}]).to_excel(writer,sheet_name='Información',index=False)
    buffer.seek(0)
    db.add(Audit(actor=role,action='exportar',object_id=forecast_id,details={'revision':body['revision']}));db.commit()
    return StreamingResponse(buffer,media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition':f'attachment; filename="Estimado_{body["origin"]}_{forecast_id[:8]}.xlsx"'})

@app.post('/api/uploads')
async def upload(source:str=Form(),mode:str=Form(),year:int=Form(2026),file:UploadFile=File(),role=Depends(identity),db=Depends(db_session)):
    can_edit(role)
    return await receive(db,file,source,mode,role,year)

@app.get('/api/uploads')
def uploads(role=Depends(identity),db=Depends(db_session)):
    return [{'id':r.id,'source':r.source,'filename':r.filename,'state':r.state,'report':r.report,
             'created_at':r.created_at.isoformat()} for r in db.scalars(select(Upload).order_by(Upload.created_at.desc()).limit(30))]
