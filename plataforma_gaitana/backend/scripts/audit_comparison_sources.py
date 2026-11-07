"""Comprobar semanas reales, estimadas y evaluadas; no modificar fuentes."""
import json
from pathlib import Path
import pandas as pd
from app import data
from app.history_eval import engineer_archive

root,folder,base=data.runtime_paths()
test=data.read(data.REVIEW/'comparacion_clima_curvas_2026.parquet')
strict=test.loc[test.grupo_comparacion.eq('principal_estricta_nominal')&test.horizonte.eq(1)]
engineer=engineer_archive(root,data.read,data.KEY)
weekly=data.weekly()
engineer=engineer.loc[engineer.finca.eq('GAITANA')&engineer.horizonte.eq(1)]
weekly=weekly.loc[weekly.finca.eq('GAITANA')]
analytic=pd.read_parquet(base/'base_analitica_proyecciones.parquet',columns=['origen','horizonte','admisible_modelo','y'])
rows=[]
for dt in pd.date_range('2025-12-29','2026-10-26',freq='W-MON'):
    actual=weekly.loc[weekly.semana_inicio.eq(dt)]
    en=engineer.loc[engineer.semana_objetivo.eq(dt)]
    te=strict.loc[strict.semana_objetivo.eq(dt)]
    ab=analytic.loc[analytic.origen.eq(dt)&analytic.horizonte.eq(1)]
    rows.append({'week':dt.strftime('%G-S%V'),'date':str(dt.date()),'real_series':len(actual),
        'real_stems':float(actual.tallos_reales.sum()),'engineer_nominal_h1':len(en),
        'test_cases':len(te),'test_comparable':len(te.dropna(subset=['y','Seleccion_pre2026','ingeniero'])),
        'analytic_admissible':int(ab.admisible_modelo.sum())})
from app.db import Session,ActiveDataset,Upload,Publication,Forecast
from sqlalchemy import select,func
with Session() as db:
    active=db.get(ActiveDataset,'vigente')
    pending=[{'source':u.source,'file':u.filename} for u in db.scalars(select(Upload).where(Upload.state=='pendiente_etl'))]
    published=db.scalar(select(func.count()).select_from(Publication))
    saved=db.scalar(select(func.count()).select_from(Forecast))
result={'active_dataset':active.dataset_id if active else None,'pending_files':pending,
        'official_publications':published,'saved_forecasts':saved,
        'archived_groups':data.records(test.groupby('grupo_comparacion').agg(cases=('horizonte','size'),since=('semana_objetivo','min'),through=('semana_objetivo','max')).reset_index()),
        'weeks':rows}
(data.STORAGE/'audit_comparison_sources.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
