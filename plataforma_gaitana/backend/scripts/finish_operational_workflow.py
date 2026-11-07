"""Finish the authorized bootstrap, refresh WebFlor, then verify a current draft."""
import json
import time
from .verify_operational import main as verify,request
from app.config import STORAGE


def main():
    first=verify('actualizacion_20261026',wait=True)
    (STORAGE/'verification_initial_sql.json').write_text(json.dumps(first,ensure_ascii=False,indent=2),encoding='utf-8')
    job_id=request('/data/webflor',{})['job_id']
    print('Actualización WebFlor solicitada:',job_id,flush=True)
    last=None;deadline=time.monotonic()+3*3600
    while True:
        job=request('/jobs/'+job_id)
        if job['message']!=last:
            last=job['message'];print('WebFlor:',last,flush=True)
        if job['state'] in ['completado','error']:break
        if time.monotonic()>deadline:raise TimeoutError('Consultar el trabajo WebFlor antes de iniciar otra actualización.')
        time.sleep(15)
    if job['state']=='error':raise RuntimeError(job['message'])
    download=job['result'].get('webflor',{})
    dataset_id=job['result'].get('dataset_id',first['dataset_id'])
    report=verify(dataset_id)
    report['webflor_job_id']=job_id;report['webflor']=download
    (STORAGE/'verification_operational.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('CIERRE VERIFICADO: SQL, WebFlor y pronóstico actualizado en borrador.',flush=True)


if __name__=='__main__':main()
