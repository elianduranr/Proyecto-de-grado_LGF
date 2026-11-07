"""Audita la nueva edición contra las predicciones ejecutadas y los objetivos reales."""
from pathlib import Path
import hashlib,json,re
import numpy as np
import pandas as pd
from docx import Document

ROOT=Path(__file__).resolve().parents[1];FOLDER=ROOT/'Trabajo escrito'
NAME='Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028'
OUT=ROOT/'Datos_analiticos_proyecto/validacion_temporal_20261028'
def sha(path):return hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
md=(FOLDER/(NAME+'.md')).read_text(encoding='utf-8')
word=Document(FOLDER/(NAME+'.docx'))
content='\n'.join([p.text for p in word.paragraphs]+[c.text for t in word.tables for r in t.rows for c in r.cells])
plan=[p.text.strip() for p in Document(ROOT/'Plan de Proyecto/Plan de proyecto_final.docx').paragraphs]
og=plan[plan.index('2.1 Objetivo general')+1]
specific=[p for p in plan[plan.index('2.2 Objetivos específicos')+1:plan.index('2.3 Alcance de la decisión')] if p]
assert og in content and len(specific)==4 and all(p in content for p in specific)
assert all(f'Respuesta a OE{i}' in content for i in range(1,5))
assert all(s in content for s in ['4.2.8. Actualización temporal','5.1.3. Comprobación ampliada','entrenamiento','retrospectiva','[PENDIENTE:'])
figures=re.findall(r'!\[(.*?)\]\((.*?)\)',md)
assert sorted(int(re.search(r'Figura (\d+)',title)[1]) for title,_ in figures)==list(range(1,21))
assert len(word.inline_shapes)==20 and all((FOLDER/path).exists() for _,path in figures)
assert all(s.width<=6.1*914400+1 and s.height<=7.8*914400+1 for s in word.inline_shapes)
pred=pd.read_parquet(OUT/'predicciones_actualizadas.parquet')
assert not pred.duplicated(['modelo','finca','producto','color','variedad','origen','horizonte']).any()
assert (pred.corte_entrenamiento<=pred.origen).all()
scores=pd.read_csv(OUT/'metricas_comparadas.csv',dtype={'horizonte':str})
for row in scores.itertuples():
    d=pred.loc[pred.periodo.eq(row.periodo)&pred.modelo.eq(row.comparacion)].dropna(subset=['ingeniero'])
    if row.horizonte!='Total':d=d.loc[d.horizonte.eq(int(row.horizonte))]
    col='ingeniero' if row.metodo=='Ingeniero' else 'media_4' if row.metodo=='Media4' else 'prediccion'
    error=d[col]-d.y
    assert len(d)==row.casos
    assert np.isclose(100*error.abs().sum()/d.y.sum(),row.WAPE)
    assert np.isclose(100*error.sum()/d.y.sum(),row.sesgo_pct)
annual=pd.read_csv(OUT/'metricas_2026_completo.csv',dtype={'horizonte':str})
for row in annual.itertuples():
    d=pred.loc[pred.modelo.eq('19_mensual_sin_clima')].dropna(subset=['ingeniero'])
    if row.horizonte!='Total':d=d.loc[d.horizonte.eq(int(row.horizonte))]
    error=d['ingeniero' if row.metodo=='Ingeniero' else 'prediccion']-d.y
    assert len(d)==row.casos
    assert np.isclose(100*error.abs().sum()/d.y.sum(),row.WAPE)
    assert np.isclose(100*error.sum()/d.y.sum(),row.sesgo_pct)
splits=pd.read_csv(OUT/'particiones_por_corte.csv')
assert (pd.to_datetime(splits.train_ultimo_cierre)<=pd.to_datetime(splits.corte)).all()
assert np.allclose(splits.train_pct_casos+splits.test_pct_casos,100)
report={'passed':True,'objetivos_verificados':5,'conclusiones_especificas':4,'figuras':20,'tablas':len(word.tables),
    'filas_metricas_recalculadas':len(scores),'separacion_temporal_verificada':True,'edicion_anterior':
    {str(p.relative_to(ROOT)):sha(p) for p in FOLDER.glob('Documento_LaGaitana_v7_revision_profesor_20261028.*')}}
(FOLDER/'Revision_v8/verificacion_final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
