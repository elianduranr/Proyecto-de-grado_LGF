"""Reconstrucción local reproducible. No consulta ni escribe SQL Server/WebFlor."""
import json
import shutil
import os
import subprocess
import sys
from pathlib import Path
import pandas as pd
from app.config import LEGACY,STORAGE
from app.etl import STAGES,SOURCE_DIRS,MASTER_DIR,sha256,save_json
from app.webflor import MAPPING,validate_report
from app.etl_sources import year_of
from app.etl_reuse import extended

ID='evaluacion_local_20261028'
ROOT=STORAGE/'datasets'/ID
PARENT=STORAGE/'datasets/769d857a-6995-457d-a161-22d199701861'


def prepare():
    if (ROOT/'manifest.json').exists():return json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    previous=json.loads((PARENT/'manifest.json').read_text(encoding='utf-8'))
    for name,output in previous['outputs'].items():
        assert sha256(PARENT/'Datos_analiticos_proyecto'/f'{name}.parquet')==output['sha256'],name
    print('Copiando fuentes y resultados locales; la versión anterior se conserva.',flush=True)
    shutil.copytree(extended(PARENT),extended(ROOT),dirs_exist_ok=True,ignore=shutil.ignore_patterns('logs','manifest.json'))
    selected={r['path']:dict(r) for r in previous['catalog']}
    # Incorporar también originales locales nuevos, sin revertir sustituciones ya recibidas.
    for source,directory in SOURCE_DIRS.items():
        for path in (LEGACY/'Datos'/directory).rglob('*.xlsx'):
            if path.name.startswith('~$'):continue
            rel=path.relative_to(LEGACY).as_posix();old=selected.get(rel)
            if old and old.get('original_mtime_ns')==path.stat().st_mtime_ns:continue
            digest=sha256(path)
            if old and old.get('original_sha256')==digest:continue
            dest=ROOT/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
            selected[rel]={'source':source,'path':rel,'sha256':digest,'original_sha256':digest,
                'bytes':path.stat().st_size,'active':True,'display_name':path.name}
    updates=[('clima','405cbd706d5c480a907cedcb0569f6cba034429db48dad9365fd06bcf6aadc70',
              'Informe Clima  2026 a sem 42.xlsx'),
             ('planos','b54b644e1482c62c384f2790cf21392d68c2722e13fe7cf87509c939e3d98663',
              'Plano de Siembras Sem 42.xlsx')]
    for source,digest,label in updates:
        path=STORAGE/'uploads'/f'{digest}.xlsx';assert sha256(path)==digest
        candidates=[r for r in selected.values() if r['source']==source and r.get('active',True) and year_of(r['path'])==2026]
        rel=candidates[0]['path'] if source=='clima' else f'Datos/{SOURCE_DIRS[source]}/2026/{label}'
        if source=='clima':
            for r in candidates:
                r['active']=False;(ROOT/r['path']).unlink(missing_ok=True)
        dest=ROOT/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
        selected[rel]={'source':source,'path':rel,'sha256':digest,'active':True,
                       'bytes':path.stat().st_size,'display_name':label,'local_received_upload':True}
    check=json.loads((STORAGE/'verification_webflor_refresh_source.json').read_text(encoding='utf-8'))
    path=STORAGE/'webflor_checks'/check['server_today']/'reporte_original.parquet'
    report=validate_report(pd.read_parquet(path),check['requested_start'],check['closed_through'])
    rel='Datos/Producción real/2026_webflor_reconsulta_local.xlsx';dest=ROOT/rel
    report[list(MAPPING)].rename(columns=MAPPING).to_excel(dest,sheet_name='BD',index=False)
    selected[rel]={'source':'produccion','path':rel,'sha256':sha256(dest),'active':True,
        'bytes':dest.stat().st_size,'display_name':dest.name,'replace_window':{
            'start':check['requested_start'],'end':check['closed_through'],'received_at':'2026-10-28T23:00:00'},
        'raw_parquet_sha256':sha256(path)}
    code={}
    for rel in {*(r for r,_ in STAGES),'Notebooks/Analisis/19_modelos_clima_y_curvas_gaitana.ipynb'}:
        dest=ROOT/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(LEGACY/rel,dest);code[rel]=sha256(dest)
    for path in (LEGACY/MASTER_DIR).glob('TablasBasicas_*.csv'):shutil.copyfile(extended(path),extended(ROOT/MASTER_DIR/path.name))
    # Sólo estadísticas, estimados y maestros independientes no cambiados.
    source_signature=lambda rows,source:{r['path']:r['sha256'] for r in rows if r.get('active',True) and r['source']==source}
    masters_unchanged=all(Path(extended(PARENT/MASTER_DIR/name)).exists() and sha256(extended(PARENT/MASTER_DIR/name))==sha256(extended(ROOT/MASTER_DIR/name))
        for name in ['TablasBasicas_Producto.csv','TablasBasicas_Color.csv','TablasBasicas_Variedad.csv'])
    completed=[i for i in [0,2,5] if masters_unchanged and previous['notebooks'].get(STAGES[i][0])==code[STAGES[i][0]]
        and (i==5 or source_signature(previous['catalog'],{0:'estadisticas',2:'estimados'}[i])==source_signature(selected.values(),{0:'estadisticas',2:'estimados'}[i]))]
    manifest={'id':ID,'state':'preparado_local','offline':True,'parent_dataset':previous['id'],
        'sources':[r for r in selected.values() if r.get('active',True)],'catalog':list(selected.values()),
        'notebooks':code,'completed_stages':completed,'reused_stages':completed.copy(),
        'policy':'Datos locales; no activar ni modificar bases SQL ni versiones anteriores.'}
    save_json(ROOT/'manifest.json',manifest)
    return manifest


def main():
    manifest=prepare();logs=ROOT/'logs_locales';logs.mkdir(exist_ok=True)
    env={**os.environ,'PYTHONPATH':str(Path(__file__).resolve().parents[1]),'PYTHONIOENCODING':'utf-8','MPLBACKEND':'Agg',
         'OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2'}
    for i,(rel,flag) in enumerate(STAGES):
        if i in manifest['completed_stages']:continue
        print(f'ETL LOCAL {i+1}/{len(STAGES)}: {Path(rel).stem}',flush=True)
        with (logs/f'{i:02d}_{Path(rel).stem}.log').open('w',encoding='utf-8') as stream:
            result=subprocess.run([sys.executable,'-u','-m','app.etl_notebook',str(ROOT/rel),str(ROOT),flag],
                cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
        if result.returncode:raise RuntimeError(f'ETL local falló: {rel}. Consulte {logs}.')
        manifest['completed_stages'].append(i);save_json(ROOT/'manifest.json',manifest)
    from app.etl_store import validate
    validate(ROOT,manifest)
    manifest['state']='validado_local';save_json(ROOT/'manifest.json',manifest)
    print(json.dumps({'root':str(ROOT),'outputs':manifest['outputs']},ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
