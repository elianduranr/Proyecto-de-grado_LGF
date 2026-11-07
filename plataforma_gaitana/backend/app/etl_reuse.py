"""Reuse only outputs whose source hashes, masters and notebook code are unchanged."""
import shutil
import json
import os
from pathlib import Path
from .db import Session, ActiveDataset, Dataset
from .config import STORAGE

SOURCE_STAGE={'estadisticas':0,'clima':1,'estimados':2,'planos':3,'produccion':4}
OUTPUTS={'estadisticas':'curvas_variedad_limpio.parquet','clima':'clima_limpio.parquet',
         'estimados':'estimados_semanales_limpio.parquet','planos':'planos_siembra_limpio.parquet',
         'produccion':'produccion_real_limpio.parquet'}


def extended(path):
    text=str(Path(path).resolve())
    return Path('\\\\?\\'+text) if os.name=='nt' and not text.startswith('\\\\?\\') else Path(text)


def reuse(workspace,manifest,stages,master_dir,projection_dir,hash_file):
    with Session() as db:
        pointer=db.get(ActiveDataset,'vigente')
        row=db.get(Dataset,pointer.dataset_id) if pointer else None
        previous=Path(row.root) if row else None
        previous=(previous if previous.is_absolute() else STORAGE/previous) if previous else None
        old=row.manifest if row else None
    if previous is None:
        # A completed, validated rebuild is also a safe source of independent artifacts,
        # even if SQL loading was interrupted. Check every recorded clean-file hash.
        for candidate in sorted((STORAGE/'datasets').glob('*/manifest.json'),reverse=True):
            document=json.loads(candidate.read_text(encoding='utf-8'))
            if document.get('state') not in ['validado','activo'] or len(document.get('completed_stages',[]))!=len(stages):continue
            folder=candidate.parent
            if all((folder/'Datos_analiticos_proyecto'/f'{name}.parquet').exists() and
                   hash_file(folder/'Datos_analiticos_proyecto'/f'{name}.parquet')==output['sha256']
                   for name,output in document.get('outputs',{}).items()) and len(document.get('outputs',{}))==5:
                previous,old=folder,document;break
        if previous is None:return
    if not previous.is_dir():return
    completed=[]
    def signature(document,source):
        return sorted((r['path'],r['sha256'],json.dumps(r.get('replace_window'),sort_keys=True)) for r in document['sources'] if r['source']==source)
    unchanged={source:signature(old,source)==signature(manifest,source) for source in SOURCE_STAGE}
    if any(r.get('replace_window') for r in manifest['sources']):
        unchanged['produccion'] &= old.get('production_window_reader_sha256')==manifest.get('production_window_reader_sha256')
    def code_equal(index):
        relative=stages[index][0]
        return old['notebooks'].get(relative)==manifest['notebooks'].get(relative)
    for source,index in SOURCE_STAGE.items():
        relative='Datos_analiticos_proyecto/'+OUTPUTS[source]
        if unchanged[source] and code_equal(index) and (previous/relative).exists():
            (workspace/relative).parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(previous/relative,workspace/relative);completed.append(index)
    masters=all((previous/master_dir/name).exists() and hash_file(previous/master_dir/name)==hash_file(workspace/master_dir/name)
                for name in ['TablasBasicas_Producto.csv','TablasBasicas_Color.csv','TablasBasicas_Variedad.csv'])
    catalog=masters and code_equal(5) and (previous/master_dir/'Catalogo_analitico').exists()
    if catalog:
        shutil.copytree(extended(previous/master_dir/'Catalogo_analitico'),extended(workspace/master_dir/'Catalogo_analitico'),dirs_exist_ok=True)
        completed.append(5)
    projections=catalog and 0 in completed and 3 in completed and unchanged['planos'] and unchanged['estadisticas'] and all(code_equal(i) for i in [6,7,8])
    if projections:
        shutil.copytree(extended(previous/projection_dir/'resultados_todos_los_anios'),extended(workspace/projection_dir/'resultados_todos_los_anios'),dirs_exist_ok=True)
        completed.extend([6,7,8])
    analytical=projections and 4 in completed and 1 in completed and unchanged['produccion'] and unchanged['clima'] and code_equal(9)
    if analytical:
        relative='Datos_analiticos_proyecto/modelo_con_proyecciones_teoricas'
        shutil.copytree(extended(previous/relative),extended(workspace/relative),dirs_exist_ok=True);completed.append(9)
        if code_equal(10):
            relative='Datos_analiticos_proyecto/modelo_diario'
            shutil.copytree(extended(previous/relative),extended(workspace/relative),dirs_exist_ok=True);completed.append(10)
    manifest['completed_stages']=completed
    manifest['reused_from']=old['id']
    manifest['reused_stages']=completed.copy()
