"""Detener sólo el publicador propio para reanudar su prefijo confirmado sin duplicados."""
import json
import psutil
from sqlalchemy import select
from app.config import STORAGE
from app.db import Session,Job,now

proof=json.loads((STORAGE/'verification_sql_transport_sources.json').read_text(encoding='utf-8'))
assert proof['passed'] and len(proof['sources'])==5
targets=[]
for process in psutil.process_iter(['cmdline']):
    command=process.info['cmdline'] or []
    if '-m' in command and command[command.index('-m')+1]=='scripts.persist_offline_validation':targets.append(process)
for process in targets:
    try:process.terminate()
    except psutil.NoSuchProcess:pass
_,alive=psutil.wait_procs(targets,timeout=10)
assert not alive
with Session.begin() as db:
    for job in db.scalars(select(Job).where(Job.kind=='etl',Job.state=='en_proceso')):
        if job.payload.get('snapshot_id')=='evaluacion_local_20261028':
            job.state='error';job.updated_at=now()
            job.message='Reanudación controlada con transporte SQL comprimido ya verificado. Se conserva el prefijo cargado y la base vigente.'
print('Publicador detenido de forma controlada; prefijo confirmado conservado.',flush=True)
