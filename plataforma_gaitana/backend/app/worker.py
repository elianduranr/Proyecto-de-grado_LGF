"""Un trabajador independiente; ejecutar con python -m app.worker."""
import logging
import time
import math
import threading
from datetime import timedelta
from sqlalchemy import select,update
from .db import Session,Job,Forecast,Line,Audit,now
from .model19 import run_forecast

log=logging.getLogger('gaitana.worker')

def progress(job_id,value,message):
    with Session.begin() as db:
        row=db.get(Job,job_id);row.progress=value;row.message=message;row.updated_at=now()

def execute(job_id):
    with Session() as db:
        job=db.get(Job,job_id);payload=job.payload;kind=job.kind
    try:
        if kind in ['etl','webflor']:
            from .etl import rebuild
            from .etl_store import persist_and_activate
            download=None
            if kind=='webflor':
                from .webflor import stage
                download=stage(payload['actor'],job_id,lambda n,m:progress(job_id,n,m))
                if not download.get('requires_rebuild',bool(download['new_rows'])):
                    with Session.begin() as db:
                        job=db.get(Job,job_id);job.state='completado';job.progress=100;job.updated_at=now()
                        job.message=download['message'];job.result={'webflor':download}
                    return
            root,manifest=rebuild(payload.get('snapshot_id',job_id),lambda n,m:progress(job_id,n,m))
            persist_and_activate(root,manifest,payload['actor'],lambda n,m:progress(job_id,n,m))
            with Session.begin() as db:
                job=db.get(Job,job_id);job.state='completado';job.progress=100
                job.message='Fuentes limpias guardadas y base analítica actualizada.'
                job.result={'dataset_id':manifest['id'],**({'webflor':download} if download else {})};job.updated_at=now()
            return
        result,metadata=run_forecast(payload['origin'],payload['variant'],lambda n,m:progress(job_id,n,m))
        progress(job_id,95,'Guardando la propuesta original y su trazabilidad')
        with Session.begin() as db:
            run=Forecast(origin=payload['origin'],variant=payload['variant'],metadata_json=metadata)
            db.add(run);db.flush()
            for r in result.itertuples(index=False):
                db.add(Line(forecast_id=run.id,product=r.producto,color=r.color,variety=r.variedad,
                    horizon=int(r.horizonte),target=str(r.semana_objetivo.date()),model_value=float(r.prediction),
                    final_value=int(math.floor(r.prediction+.5)),theory=float(r.teoria_modelo) if r.teoria_modelo==r.teoria_modelo else None,route=r.route))
            job=db.get(Job,job_id);job.state='completado';job.progress=100;job.message='Propuesta lista para revisión; aún no publicada.'
            job.result={'forecast_id':run.id};job.updated_at=now()
            db.add(Audit(actor=payload['actor'],action='pronostico_generado',object_id=run.id,details=metadata))
    except Exception as exc:
        log.exception('Error en trabajo %s',job_id)
        with Session.begin() as db:
            job=db.get(Job,job_id);job.state='error'
            job.message=str(exc) if isinstance(exc,ValueError) else 'No se completó el trabajo. Revisa el log del trabajador; los datos vigentes se conservan.'
            job.updated_at=now()

def main():
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    while True:
        try:
            with Session.begin() as db:
                stale=db.scalars(select(Job).where(Job.state=='en_proceso',Job.updated_at<now()-timedelta(hours=2))).all()
                for job in stale:job.state='error';job.message='Ejecución interrumpida. Puede solicitarse una nueva simulación.'
                row=db.scalar(select(Job).where(Job.state=='pendiente').order_by(Job.created_at))
                job_id=None
                if row and db.execute(update(Job).where(Job.id==row.id,Job.state=='pendiente').values(state='en_proceso',updated_at=now())).rowcount==1:
                    job_id=row.id
            if job_id:execute(job_id)
            else:time.sleep(2)
        except KeyboardInterrupt:return
        except Exception:
            log.exception('Trabajador en espera: revisa conexión y migraciones');time.sleep(5)

if __name__=='__main__':main()
