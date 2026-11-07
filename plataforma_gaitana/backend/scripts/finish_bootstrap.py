"""Monitor the initial CLI rebuild, persist its result and expose progress to the UI."""
import argparse
import json
import time
from app.config import STORAGE
from app.db import Session, Job, now
from app.etl_store import persist_and_activate

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('snapshot_id');parser.add_argument('--replace');args=parser.parse_args()
    if any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.snapshot_id):
        raise ValueError('Identificador no válido')
    root=STORAGE/'datasets'/args.snapshot_id
    job_id='etl_'+args.snapshot_id
    if len(job_id)>36:raise ValueError('Identificador demasiado largo')
    with Session.begin() as db:
        if args.replace:
            replaced=db.get(Job,'etl_'+args.replace)
            if replaced and replaced.kind=='etl' and replaced.state in ['pendiente','en_proceso','error']:
                replaced.state='error';replaced.updated_at=now()
                replaced.message=f'Procesamiento reemplazado antes de activación por {args.snapshot_id}, que incorpora todas las hojas de detalle verificadas.'
        job=db.get(Job,job_id)
        if not job:db.add(Job(id=job_id,kind='etl',state='en_proceso',payload={'actor':'administrador','snapshot_id':args.snapshot_id}))
        else:
            job.state='en_proceso';job.updated_at=now()
            job.message='Reanudando la validación y los bloques SQL pendientes; se conservan los bloques confirmados.'
    def progress(value,message):
        with Session.begin() as db:
            job=db.get(Job,job_id);job.progress=value;job.message=message;job.updated_at=now()
        print(value,message,flush=True)
    try:
        while True:
            manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
            if manifest['state']=='error':raise ValueError('Una etapa del ETL falló; consulta los logs de la ejecución. Los datos vigentes no cambiaron.')
            if len(manifest['completed_stages'])==11:break
            done=len(manifest['completed_stages'])
            logs=sorted((root/'logs').glob('*.log'))
            current=logs[-1].stem if logs else 'archivo de fuentes'
            progress(10+int(done*65/11),f'ETL {done+1}/11: {current}')
            time.sleep(15)
        persist_and_activate(root,manifest,progress=progress)
        with Session.begin() as db:
            job=db.get(Job,job_id);job.state='completado';job.progress=100;job.updated_at=now()
            job.message='Fuentes limpias guardadas en EP y base analítica actualizada.'
            job.result={'dataset_id':args.snapshot_id}
        print('Base activada:',manifest['latest_origin'],flush=True)
    except Exception as exc:
        with Session.begin() as db:
            job=db.get(Job,job_id);job.state='error';job.updated_at=now()
            job.message=str(exc) if isinstance(exc,ValueError) else 'Falló la carga SQL. La base vigente se conserva; revisar el log.'
        raise
