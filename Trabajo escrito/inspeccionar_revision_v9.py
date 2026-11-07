"""Inventario de evidencia para revisión editorial; no modifica datos ni modelos."""
from pathlib import Path
import json, hashlib, shutil
import pandas as pd
import pyarrow.parquet as pq
import sys
sys.stdout.reconfigure(encoding='utf8')

F=Path(__file__).resolve().parent; R=F.parent; O=F/'Revision_v9';O.mkdir(exist_ok=True)
old='Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028'
backup=O/'Version_inicial';backup.mkdir(exist_ok=True)
hashes={}
for ext in ['md','docx','pdf']:
    p=F/f'{old}.{ext}';hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
    dst=backup/p.name
    if not dst.exists():shutil.copy2(p,dst)
    assert hashlib.sha256(dst.read_bytes()).hexdigest()==hashes[str(p.relative_to(R))]
(O/'version_inicial_sha256.json').write_text(json.dumps(hashes,indent=2),encoding='utf8')
snapshot=R/'plataforma_gaitana/storage/datasets/evaluacion_local_20261028'
m=json.loads((snapshot/'manifest.json').read_text(encoding='utf8'))
print('OUTPUTS',json.dumps(m.get('outputs'),ensure_ascii=False,indent=2))
for base in [snapshot]:
    print('FILES',str(base))
    for p in base.rglob('*'):
        if p.is_file() and p.suffix in ['.parquet','.csv','.json'] and not any(x in p.parts for x in ['Datos','originals']):
            if len(p.relative_to(base).parts)>5:continue
            if len(p.relative_to(base).parts)>2:continue
            print(str(p.relative_to(base)))
            if p.suffix=='.parquet' and any(x in p.stem.lower() for x in ['base_analitica','semanal','curva','corte','estadistic','proyeccion']):
                pf=pq.ParquetFile(str(p));print('  ',pf.metadata.num_rows,pf.schema_arrow.names)
print('AUDIT GROUPS')
a=pd.read_csv(F/'Revision_v7/auditoria_metricas_v7.csv')
for stage,g in a.groupby('etapa',sort=False):
    print(stage,':',', '.join(g.modelo.astype(str).unique()))
print('OLD FIGURE LOGIC')
for p in [F/'revisar_tesis_v7.py',F/'actualizar_resultados.py']:
    s=p.read_text(encoding='utf8')
    for key in ['cobertura_teoria_casos','curva_y_soporte','clima_asociaciones','6b']:
        i=s.find(key)
        if i>=0:print(p.name,key,s[max(0,i-1200):i+400])
