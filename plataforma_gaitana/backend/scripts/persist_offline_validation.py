"""Publicar en EP la copia reconstruida, validando que no cambió la base de partida."""
import json
import shutil
import time
from pathlib import Path
from sqlalchemy import select,func
from app.config import STORAGE
from app.db import Session,ActiveDataset,Upload,Job,now
from app.etl import sha256,save_json
from app.etl_store import persist_and_activate
from app.clean_tables import CLEAN_TABLES

root=STORAGE/'datasets/evaluacion_local_20261028'
with Session.begin() as db:
    running=db.scalars(select(Job).where(Job.state.in_(['pendiente','en_proceso']))).all()
    if running:raise ValueError('Existe otro trabajo activo; no se inicia una carga concurrente.')
    job=Job(kind='etl',state='en_proceso',payload={'actor':'ingeniero','snapshot_id':root.name},
        message='Reconstruyendo y validando las fuentes actualizadas antes de activar SQL.',progress=10)
    db.add(job);db.flush();job_id=job.id

def progress(n,message):
    print(f'{n}% · {message}',flush=True)
    with Session.begin() as db:
        job=db.get(Job,job_id);job.progress=n;job.message=message;job.updated_at=now()

import atexit
finished=False
def mark_interrupted():
    if not finished:
        with Session.begin() as db:
            job=db.get(Job,job_id);job.state='error';job.updated_at=now()
            job.message='La activación se interrumpió; se conserva la base vigente. Revisar el log de validación.'
atexit.register(mark_interrupted)
while True:
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('state') in ['validado_local','validado','activo']:break
    with Session.begin() as db:db.get(Job,job_id).updated_at=now()
    time.sleep(10)
assert manifest['state'] in ['validado_local','validado','activo']
previous=json.loads((STORAGE/'datasets'/manifest['parent_dataset']/'manifest.json').read_text(encoding='utf-8'))
prior={r['path']:r for r in previous['catalog']}
with Session() as db:
    active=db.get(ActiveDataset,'vigente')
    if active.dataset_id not in [manifest['parent_dataset'],manifest['id']]:
        raise ValueError('La base activa cambió durante la reconstrucción. Hay que revisar el empalme antes de activar esta copia.')
    receipts=db.scalars(select(Upload).where(Upload.state=='pendiente_etl')).all()
    manifest['uploads']=[r.id for r in receipts if any(s['source']==r.source and s['sha256']==r.sha256 for s in manifest['sources'])]
for row in manifest['catalog']:
    if row['path'] in prior and not row.get('original_sha256'):
        row['original_sha256']=prior[row['path']].get('original_sha256',prior[row['path']]['sha256'])
    if row.get('active',True):
        path=root/row['path'];assert sha256(path)==row['sha256']
        frozen=STORAGE/'source_archive'/f'{row["sha256"]}.xlsx'
        if not frozen.exists():shutil.copyfile(path,frozen)
manifest['policy']='Reconstrucción local versionada; persistencia y activación SQL posteriores a validación, conservando la base anterior.'
save_json(root/'manifest.json',manifest)
persist_and_activate(root,manifest,'ingeniero',progress)
checks=[]
with Session() as db:
    assert db.get(ActiveDataset,'vigente').dataset_id==manifest['id']
    for name,item in manifest['outputs'].items():
        table=CLEAN_TABLES[name]
        q=select(func.count()).select_from(table).where(table.c.dataset_id==item['sql_dataset_id'],table.c.row_number<item['rows'])
        count=db.scalar(q);assert count==item['rows'],name
        checks.append({'fuente':name,'sql_rows':count,'parquet_rows':item['rows'],'matched':True})
    table=CLEAN_TABLES['produccion_real_limpio'];item=manifest['outputs']['produccion_real_limpio']
    stems=db.scalar(select(func.sum(table.c.tallos)).where(table.c.dataset_id==item['sql_dataset_id'],table.c.row_number<item['rows']))
import pyarrow.parquet as pq
expected=sum(batch.column(0).to_pandas().sum() for batch in pq.ParquetFile(root/'Datos_analiticos_proyecto/produccion_real_limpio.parquet').iter_batches(columns=['tallos']))
assert int(stems)==int(expected)
result={'passed':True,'dataset_id':manifest['id'],'checks':checks,'sql_stems':int(stems),'parquet_stems':int(expected)}
(STORAGE/'verification_sql_evaluacion_20261028.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
with Session.begin() as db:
    job=db.get(Job,job_id);job.state='completado';job.progress=100;job.updated_at=now()
    job.message='Fuentes actualizadas, activadas y verificadas en SQL EP.';job.result=result
finished=True
