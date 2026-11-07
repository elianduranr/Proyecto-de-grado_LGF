"""Actualizar el control de inventario para admitir planos nuevos y verificar su fuente."""
from pathlib import Path
import ast,json
from app.config import LEGACY,STORAGE
from app.etl import sha256,save_json

REL=Path('Notebooks/Proyecciones Teoricas Propias/Auditoria_calidad_curvas.ipynb')
CODE='''from pathlib import Path
import pandas as pd
import numpy as np
from IPython.display import display

def verificar_conservacion(antes, despues, planos):
    dims=['plano','finca','horizonte']
    aa=antes.groupby(dims,dropna=False).plantas.sum()
    dd=despues.groupby(dims,dropna=False).plantas.sum()
    # Los grupos anteriores deben seguir presentes y conservar sus cantidades.
    assert aa.index.difference(dd.index).empty, 'Desaparecieron planos, fincas u horizontes de la referencia.'
    assert np.allclose(aa.to_numpy(),dd.reindex(aa.index).to_numpy()), 'Cambió el inventario de los planos anteriores.'
    # Los planos incorporados se comprueban contra el inventario de origen.
    fuente=planos.loc[planos.version_seleccionada].copy()
    fuente['plantas']=fuente.plantas.where(fuente.plantas.ge(0))
    esperado=fuente.groupby(['archivo','finca'],dropna=False).plantas.sum().rename('esperado').reset_index().rename(columns={'archivo':'plano'})
    actual=dd.rename('actual').reset_index()
    assert set(map(tuple,actual[['plano','finca']].drop_duplicates().to_numpy()))==set(map(tuple,esperado[['plano','finca']].to_numpy())), 'La proyección y el inventario fuente no contienen las mismas fincas y planos.'
    control=actual.merge(esperado,on=['plano','finca'],how='left',validate='many_to_one')
    assert np.allclose(control.actual,control.esperado), 'La proyección no conserva las plantas de su plano fuente.'
    return len(dd.index.difference(aa.index))

ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'Datos_analiticos_proyecto').exists())
PROY=ROOT/'Notebooks/Proyecciones Teoricas Propias/resultados_todos_los_anios'
controles=[]
for anio in range(2021,2027):
    antes=pd.read_parquet(PROY/'auditoria_calidad'/f'cobertura_antes_{anio}.parquet')
    despues=pd.read_parquet(PROY/str(anio)/'proyecciones_teoricas.parquet')
    despues=despues.loc[despues.version_seleccionada]
    planos=pd.read_parquet(PROY/str(anio)/'planos.parquet')
    nuevos=verificar_conservacion(antes,despues,planos)
    comunes=despues.loc[despues.plano.isin(antes.plano.unique())]
    controles.append({'anio':anio,'plantas_conservadas':True,'grupos_plano_finca_horizonte_nuevos':nuevos,
        'cobertura_antes_exposiciones':antes.loc[antes.estado.eq('proyectada'),'plantas'].sum()/antes.plantas.sum(),
        'cobertura_despues_exposiciones':comunes.loc[comunes.estado.eq('proyectada'),'plantas'].sum()/comunes.plantas.sum()})
conservacion=pd.DataFrame(controles)
display(conservacion)
conservacion.to_excel(PROY/'auditoria_calidad/conservacion_y_cobertura.xlsx',index=False)
print('Se conservan las plantas de cada plano, finca y horizonte. Los planos nuevos se verifican contra su fuente; el antes/después compara sólo planos comunes. Las exposiciones no son plantas físicas únicas.')
'''

def main():
    path=LEGACY/REL
    nb=json.loads(path.read_text(encoding='utf-8'))
    nb['cells'][13]['source']=CODE.splitlines(keepends=True)
    nb['cells'][13]['outputs']=[];nb['cells'][13]['execution_count']=None
    path.write_text(json.dumps(nb,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
    snapshot=STORAGE/'datasets/evaluacion_local_20261028'
    frozen=snapshot/REL;frozen.write_bytes(path.read_bytes())
    manifest=json.loads((snapshot/'manifest.json').read_text(encoding='utf-8'))
    manifest['notebooks'][REL.as_posix()]=sha256(frozen)
    manifest.setdefault('audit_changes',[]).append({'notebook':REL.as_posix(),'reason':'Control de conservación admite planos añadidos, exige preservar los anteriores y coteja todos contra su fuente. No cambia las proyecciones.'})
    save_json(snapshot/'manifest.json',manifest)
    # Prueba de regresión del control real, incluyendo pérdida y alteración.
    import pandas as pd,numpy as np
    node=next(n for n in ast.parse(CODE).body if isinstance(n,ast.FunctionDef))
    ns={'pd':pd,'np':np};exec(compile(ast.Module(body=[node],type_ignores=[]),'audit_inventory','exec'),ns)
    before=pd.DataFrame([{'plano':'S1','finca':'GAITANA','horizonte':h,'plantas':100} for h in [1,2]])
    added=pd.DataFrame([{'plano':'S2','finca':'GAITANA','horizonte':h,'plantas':200} for h in [1,2]])
    after=pd.concat([before,added],ignore_index=True)
    source=pd.DataFrame({'archivo':['S1','S2'],'finca':['GAITANA']*2,'plantas':[100,200],'version_seleccionada':[True,True]})
    assert ns['verificar_conservacion'](before,after,source)==2
    for bad in [added,after.assign(plantas=[90,100,200,200]),after.assign(plantas=[100,100,190,200])]:
        try:ns['verificar_conservacion'](before,bad,source)
        except AssertionError:pass
        else:raise AssertionError('El control no detectó pérdida o modificación de inventario.')
    print('Control probado: admite planos nuevos y detecta desaparición o cambios de cantidades.')

if __name__=='__main__':main()
