from pathlib import Path
from zipfile import BadZipFile
import hashlib
import re
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool
from xml.etree.ElementTree import ParseError
from .config import STORAGE
from .db import Upload, Audit, SourceFile
from .xlsx_header import inspect_workbook

SOURCES={'clima':{'completo','adicional'},'produccion':{'completo','adicional'},
         'planos':{'adicional'},'estadisticas':{'completo'},'estimados':{'completo'}}
MAX_BYTES=300*1024*1024

async def receive(db,file,source,mode,actor,year=2026):
    if source not in SOURCES or mode not in SOURCES[source]:
        raise HTTPException(422,'Modalidad no válida para esta fuente.')
    if year not in range(2021,2027):
        raise HTTPException(422,'Los formatos de esta versión están validados para 2021–2026.')
    await run_in_threadpool(check_running_job,db)
    name=Path((file.filename or '').replace('\\','/')).name
    declared_years={int(value) for value in re.findall(r'(?<!\d)(20\d{2})(?!\d)',name)}
    if declared_years and declared_years!={year}:
        raise HTTPException(422,'El año seleccionado debe coincidir con el año del nombre del archivo.')
    if not name.lower().endswith('.xlsx'):
        raise HTTPException(422,'El primer prototipo recibe libros .xlsx; no transforma otros formatos silenciosamente.')
    folder=STORAGE/'uploads';folder.mkdir(exist_ok=True)
    from .db import uid
    temp=folder/(uid()+'.part');sha=hashlib.sha256();size=0
    try:
        with temp.open('wb') as stream:
            while block:=await file.read(1024*1024):
                size+=len(block)
                if size>MAX_BYTES:raise HTTPException(413,'El archivo supera 300 MB.')
                sha.update(block);stream.write(block)
        return await run_in_threadpool(register,db,temp,sha.hexdigest(),size,name,source,mode,actor,year)
    finally:
        temp.unlink(missing_ok=True)


def check_running_job(db):
    from .db import Job
    if db.scalar(select(Job).where(Job.state.in_(['pendiente','en_proceso']))):
        raise HTTPException(409,'Espera a que termine el procesamiento o pronóstico actual antes de cargar otra fuente.')


def register(db,temp,digest,size,name,source,mode,actor,year):
    """Inspección y SQL fuera del bucle HTTP; la limpieza completa pertenece al ETL."""
    try:
        check_running_job(db)
        old=db.scalar(select(Upload).where(Upload.source==source,Upload.sha256==digest))
        if old:return {'id':old.id,'state':old.state,'duplicate':True,'report':old.report}
        known=db.scalars(select(SourceFile).where(SourceFile.source==source,SourceFile.sha256==digest,SourceFile.active==1)).all()
        if known:
            from .etl_sources import year_of
            if not any(year_of(row.path)==year for row in known):
                raise HTTPException(422,'El año seleccionado no corresponde a este archivo ya procesado.')
            report={'bytes':size,'year':year,'dataset_id':known[0].dataset_id,
                    'message':'Este archivo ya pertenece a los datos vigentes. No necesita volver a procesarse.'}
            row=Upload(source=source,filename=name,sha256=digest,mode=mode,state='sin_cambios',report=report)
            db.add(row);db.flush();db.add(Audit(actor=actor,action='archivo_sin_cambios',object_id=row.id,details={'source':source,'hash':digest}));db.commit()
            return {'id':row.id,'state':row.state,'duplicate':True,'report':report}
        if mode=='completo' and source in ['clima','produccion','estadisticas']:
            from .etl_sources import family
            pending=db.scalars(select(Upload).where(Upload.source==source,Upload.mode=='completo',Upload.state=='pendiente_etl')).all()
            if any(r.report.get('year')==year and (source!='estadisticas' or family(r.filename)==family(name)) for r in pending):
                raise HTTPException(409,'Ya hay un archivo completo pendiente para esta fuente, año y familia. Procéselo primero; no se recibirán dos reemplazos del mismo alcance.')
        sheets=inspect_workbook(temp)
        folder=STORAGE/'uploads'
        final=folder/(digest+'.xlsx');temp.replace(final)
        report={'bytes':size,'sheets':sheets,'year':year,'message':'Archivo archivado. Ejecuta Procesar archivos para validar y activar esta carga junto con las demás fuentes; todavía no modifica los datos vigentes.'}
        row=Upload(source=source,filename=name,sha256=digest,mode=mode,state='pendiente_etl',report=report)
        db.add(row);db.flush();db.add(Audit(actor=actor,action='archivo_recibido',object_id=row.id,details={'source':source,'hash':digest}));db.commit()
        return {'id':row.id,'state':row.state,'duplicate':False,'report':report}
    except IntegrityError:
        db.rollback()
        old=db.scalar(select(Upload).where(Upload.source==source,Upload.sha256==digest))
        if old:return {'id':old.id,'state':old.state,'duplicate':True,'report':old.report}
        raise
    except (BadZipFile,ParseError,KeyError,ValueError) as exc:
        raise HTTPException(422,str(exc) if isinstance(exc,ValueError) else 'No fue posible leer el índice del libro Excel.')
