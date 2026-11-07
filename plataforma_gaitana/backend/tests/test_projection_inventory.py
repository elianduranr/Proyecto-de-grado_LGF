"""El inventario admite planos añadidos, sin tolerar pérdida ni alteración de plantas."""
import ast,json
import numpy as np
import pandas as pd
import pytest
from app.config import LEGACY


def control():
    path=LEGACY/'Notebooks/Proyecciones Teoricas Propias/Auditoria_calidad_curvas.ipynb'
    notebook=json.loads(path.read_text(encoding='utf-8'))
    code='\n'.join(''.join(c['source']) for c in notebook['cells'] if c['cell_type']=='code')
    function=next(n for n in ast.parse(code).body if isinstance(n,ast.FunctionDef) and n.name=='verificar_conservacion')
    namespace={'pd':pd,'np':np}
    exec(compile(ast.Module(body=[function],type_ignores=[]),str(path),'exec'),namespace)
    return namespace['verificar_conservacion']


def example():
    before=pd.DataFrame([{'plano':'S41','finca':'GAITANA','horizonte':h,'plantas':100} for h in [1,2]])
    new=pd.DataFrame([{'plano':'S42','finca':'GAITANA','horizonte':h,'plantas':200} for h in [1,2]])
    source=pd.DataFrame({'archivo':['S41','S42'],'finca':['GAITANA']*2,'plantas':[100,200],'version_seleccionada':[True,True]})
    return before,pd.concat([before,new],ignore_index=True),source


def test_new_plan_is_checked_against_source_instead_of_old_plan_count():
    before,after,source=example()
    assert control()(before,after,source)==2


@pytest.mark.parametrize('failure',['missing','old_quantity','new_quantity'])
def test_inventory_control_rejects_missing_or_changed_quantities(failure):
    before,after,source=example()
    if failure=='missing':after=after.loc[after.plano.eq('S42')]
    else:after.loc[0 if failure=='old_quantity' else 2,'plantas']-=10
    with pytest.raises(AssertionError):control()(before,after,source)
