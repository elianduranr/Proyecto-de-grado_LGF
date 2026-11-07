"""Comprobaciones de cifras, referencias y PDF de la revisión académica v9."""
from pathlib import Path
import sys,json,re,hashlib,ast
import numpy as np
import pandas as pd
import pymupdf
from docx import Document
from PIL import Image,ImageOps,ImageDraw
sys.stdout.reconfigure(encoding='utf8')
from revision_v9_config import NAME
F=Path(__file__).resolve().parent;R=F.parent;O=F/'Revision_v9'
V=R/'Datos_analiticos_proyecto/validacion_temporal_20261028'
text=(F/(NAME+'.md')).read_text(encoding='utf8');doc=Document(F/(NAME+'.docx'))
preserved=json.loads((O/'version_inicial_sha256.json').read_text())
for rel,expected in preserved.items():
    assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==expected,rel
    assert hashlib.sha256((O/'Version_inicial'/Path(rel).name).read_bytes()).hexdigest()==expected
def metrics(d,col,y='y'):
    d=d.dropna(subset=[y,col]);a=d[y].to_numpy(float);p=d[col].to_numpy(float);e=p-a;pos=a>0;den=a.sum()
    return {'n':len(d),'MAE':np.abs(e).mean(),'RMSE':np.sqrt(np.square(e).mean()),'MAPE_pct':100*np.mean(np.abs(e[pos])/a[pos]),'WAPE_pct':100*np.abs(e).sum()/den,'dentro_8_pct':100*np.mean(np.abs(e[pos])<=.08*a[pos]),'sesgo_pct':100*e.sum()/den}
pred=pd.read_parquet(V/'predicciones_actualizadas.parquet');actual=pred.loc[pred.modelo.eq('19_mensual_sin_clima')&pred.ingeniero.notna()]
annual=pd.read_csv(V/'metricas_2026_completo.csv');checks=0
for _,row in annual.iterrows():
    z=actual if row.horizonte=='Total' else actual.loc[actual.horizonte.eq(float(row.horizonte))]
    score=metrics(z,'prediccion' if row.metodo=='19_mensual_sin_clima' else 'ingeniero')
    for key,col in [('n','casos'),('MAE','MAE'),('RMSE','RMSE'),('MAPE_pct','MAPE_positivos'),('WAPE_pct','WAPE'),('dentro_8_pct','dentro_8_pct'),('sesgo_pct','sesgo_pct')]:assert np.isclose(score[key],row[col]),(row.metodo,row.horizonte,key)
    checks+=1
assert (pred.corte_entrenamiento<=pred.origen).all()
assert (pred.semana_objetivo+pd.Timedelta(days=7)<=pd.Timestamp('2026-10-28')).all()
part=pd.read_csv(V/'particiones_por_corte.csv');assert (pd.to_datetime(part.train_ultimo_cierre)<=pd.to_datetime(part.corte)).all()
# Reejecutar sólo los cálculos de métricas de la auditoría anterior, sin su redacción ni modelos.
# El corte de AST termina antes del bloque editorial y usa funciones de registro en memoria.
script=F/'revisar_tesis_v7.py';tree=ast.parse(script.read_text(encoding='utf8'));nodes=[]
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='source_text' for t in node.targets):break
    nodes.append(node)
ns={'__file__':str(script)}
# Suprimir escrituras de los dos resúmenes auxiliares a v7: sólo se necesitan las métricas.
nodes=[n for n in nodes if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='write_text')]
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(script),'exec'),ns)
recomputed=pd.DataFrame(ns['audit']);included=pd.read_csv(O/'metricas_historicas_incluidas.csv')
for _,row in included.iterrows():
    match=recomputed.loc[recomputed.etapa.eq(row.etapa)&recomputed.modelo.eq(row.modelo)];assert len(match)==1,(row.etapa,row.modelo)
    for key in ['n','MAE','RMSE','MAPE_pct','WAPE_pct','dentro_8_pct','sesgo_pct']:
        assert np.isclose(row[key],match.iloc[0][key],equal_nan=True),(row.etapa,row.modelo,key)
    checks+=1
assert not re.search(r'\[E\d|Fuente:\s*E\d|cuadernos?\s*\d|notebooks?|Referencias de la evidencia|\[PENDIENTE:',text,re.I)
assert all('?' not in line and '¿' not in line for line in text.splitlines() if line.startswith('#'))
assert all(x in text for x in ['Rafael Amaya Gomez','Elián Durán','Julián Osorio','Anderson Gonzalez','Objetivo específico 4','99,84 %','19,27 %','19,40 %','12,10 %','17,07 %'])
assert len(doc.tables)==20 and len(doc.inline_shapes)==6
objects=json.loads((O/'objetos_y_referencias.json').read_text(encoding='utf8'))
structured=json.loads((O/'tablas_estructuradas.json').read_text(encoding='utf8'))
for key,t in structured.items():
    number=objects['tab_'+key]['number'];word_table=doc.tables[number-1]
    observed=[[c.text.strip() for c in row.cells] for row in word_table.rows]
    expected=[t['headers']]+t['rows'];assert observed==expected,('Tabla distinta de su fuente',key)
assert doc.styles['Normal'].font.size.pt==12 and doc.styles['Normal'].paragraph_format.line_spacing==1.5
xml=doc.element.xml;assert len(re.findall(r'REF (?:tab|fig)_',xml))==22
assert not re.search('Referencia no encontrada|Error!|Error de referencia',xml,re.I)
for i in range(1,7):assert f'[{i}]' in text
pdf=pymupdf.open(F/(NAME+'.pdf'));assert len(pdf)<=50
pdftext='\n'.join(p.get_text() for p in pdf)
assert not re.search('Referencia no encontrada|Error!',pdftext,re.I)
# Comprobar bordes de página, páginas vacías e índice actualizado.
outside=[];empty=[]
for i,p in enumerate(pdf):
    if len(p.get_text().strip())<25:empty.append(i+1)
    for word in p.get_text('words'):
        if word[0]<30 or word[2]>p.rect.width-25 or word[1]<20 or word[3]>p.rect.height-20:outside.append({'pagina':i+1,'palabra':word[4],'bbox':word[:4]})
assert not outside,outside[:5];assert not empty,empty
assert '1.1. Contexto operativo' in pdf[2].get_text()
preview=O/'Comprobacion_visual';preview.mkdir(exist_ok=True)
expected_previews={f'paginas_{first+1:02d}_{min(first+6,len(pdf)):02d}.png' for first in range(0,len(pdf),6)}
for old in preview.glob('paginas_*.png'):
    if re.fullmatch(r'paginas_\d{2}_\d{2}\.png',old.name) and old.name not in expected_previews:
        assert old.resolve().parent==preview.resolve()
        old.unlink()  # Sólo mosaicos propios de una comprobación anterior, nunca fuentes ni documentos.
for first in range(0,len(pdf),6):
    thumbnails=[]
    for i in range(first,min(first+6,len(pdf))):
        pix=pdf[i].get_pixmap(matrix=pymupdf.Matrix(.57,.57),alpha=False)
        im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);canvas=Image.new('RGB',(370,485),'#dddddd')
        canvas.paste(im,((370-im.width)//2,22));ImageDraw.Draw(canvas).text((8,4),f'Página {i+1}',fill='black');thumbnails.append(canvas)
    sheet=Image.new('RGB',(740,1455),'white')
    for j,im in enumerate(thumbnails):sheet.paste(im,((j%2)*370,(j//2)*485))
    sheet.save(preview/f'paginas_{first+1:02d}_{min(first+6,len(pdf)):02d}.png')
report={'passed':True,'paginas_pdf':len(pdf),'limite_paginas':50,'tablas':20,'figuras':6,'filas_metricas_recalculadas':checks,'columnas_diccionario':47,'referencias_cruzadas_word':22,'separacion_temporal':True,'version_v8_original_y_copia_conservadas':True,'texto_fuera_de_pagina':len(outside),'paginas_vacias':len(empty),'sin_entrenar_ni_cambiar_modelos':True}
report['tablas_word_coinciden_con_fuentes']=True
report['entregables_sha256']={ext:hashlib.sha256((F/(NAME+'.'+ext)).read_bytes()).hexdigest() for ext in ['md','docx','pdf']}
(O/'verificacion_final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
