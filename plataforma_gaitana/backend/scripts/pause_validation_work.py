"""Cerrar el estado del trabajo detenido explícitamente, sin alterar datos ni pronósticos."""
import json
from sqlalchemy import select
from app.db import Session,Job,ActiveDataset,now
from app.config import STORAGE

with Session.begin() as db:
    stopped=[]
    for job in db.scalars(select(Job).where(Job.state.in_(['pendiente','en_proceso']),Job.kind=='etl')):
        if job.payload.get('snapshot_id')=='evaluacion_local_20261028':
            job.state='error';job.updated_at=now()
            job.message='Detenido por solicitud del usuario para cerrar el computador. Etapas completadas conservadas; retomar la copia evaluacion_local_20261028.'
            stopped.append(job.id)
    active=db.get(ActiveDataset,'vigente')
    result={'paused_by_user':True,'jobs_stopped':stopped,'active_dataset':active.dataset_id if active else None}
(STORAGE/'pausa_20261028.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
