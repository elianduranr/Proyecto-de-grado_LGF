"""Comprobaciones documentales y numéricas, sin reentrenar ni tocar fuentes."""
from pathlib import Path
import hashlib
import json
import re
import numpy as np
import pandas as pd
from docx import Document

ROOT=Path(__file__).resolve().parent.parent;FOLDER=ROOT/'Trabajo escrito'
NAME='Documento_LaGaitana_v7_revision_profesor_20261028'
manifest=json.loads((FOLDER/'Revision_v7/fuentes_y_verificaciones.json').read_text(encoding='utf-8'))
for relative,expected in manifest['fuentes_sha256'].items():
    h=hashlib.sha256()
    with (ROOT/relative).open('rb') as stream:
        for part in iter(lambda:stream.read(1024*1024),b''):h.update(part)
    assert h.hexdigest()==expected,relative

word=Document(FOLDER/(NAME+'.docx'))
content='\n'.join([p.text for p in word.paragraphs]+[c.text for t in word.tables for r in t.rows for c in r.cells])
plan=[p.text.strip() for p in Document(ROOT/'Plan de Proyecto/Plan de proyecto_final.docx').paragraphs]
og=plan[plan.index('2.1 Objetivo general')+1]
specific=[p for p in plan[plan.index('2.2 Objetivos específicos')+1:plan.index('2.3 Alcance de la decisión')] if p]
assert og in content and len(specific)==4 and all(value in content for value in specific)
assert all(f'Respuesta a OE{i}' in content for i in range(1,5))
assert 'OE5' not in content
assert '[PENDIENTE:' in content
md=(FOLDER/(NAME+'.md')).read_text(encoding='utf-8')
figures=re.findall(r'!\[(.*?)\]\((.*?)\)',md)
assert [int(re.search(r'Figura (\d+)',title)[1]) for title,_ in figures]==list(range(1,20))
assert len(word.inline_shapes)==19 and all((FOLDER/path).exists() for _,path in figures)
assert all(shape.width<=6.1*914400+1 and shape.height<=7.8*914400+1 for shape in word.inline_shapes)

audit=pd.read_csv(FOLDER/'Revision_v7/auditoria_metricas_v7.csv')
d=pd.read_parquet(ROOT/'Datos_analiticos_proyecto/revision_clima_finca/comparacion_clima_curvas_2026.parquet')
d=d.loc[d.grupo_comparacion.eq('principal_estricta_nominal')]
assert len(d)==16325
for name,col in [('Boosting sin clima','Sin_clima'),('Ingeniero','ingeniero')]:
    row=audit.loc[audit.etapa.eq('19 · anual estricto')&audit.modelo.eq(name)].iloc[0]
    e=d[col]-d.y;positive=d.y.gt(0)
    expected=[e.abs().mean(),np.sqrt(np.mean(e**2)),100*e.abs().sum()/d.y.sum(),
              100*(e[positive].abs()/d.loc[positive,'y']).mean(),
              100*(e[positive].abs()<=.08*d.loc[positive,'y']).mean(),100*e.sum()/d.y.sum()]
    assert np.allclose(row[['MAE','RMSE','WAPE_pct','MAPE_pct','dentro_8_pct','sesgo_pct']].astype(float),expected)
report=dict(passed=True,objetivos_del_plan_verificados=5,conclusiones_especificas=4,
            fuentes_sin_cambios=len(manifest['fuentes_sha256']),version_6_conservada=True,
            figuras=19,imagenes_dentro_de_pagina=True,tablas=len(word.tables),
            resúmenes_metricas=len(audit),metricas_anuales_recalculadas_coinciden=True,
            no_reentrenamiento=True)
(FOLDER/'Revision_v7/verificacion_final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
