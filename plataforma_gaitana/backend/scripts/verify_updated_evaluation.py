"""Contrastar la API, las tablas ejecutadas y una propuesta real del mismo modelo."""
import json
from urllib.request import urlopen
import numpy as np
import pandas as pd
from app.config import LEGACY,STORAGE
from app.data import KEY

def get(path):
    with urlopen('http://127.0.0.1:8000/api'+path,timeout=180) as response:return json.load(response)

out=LEGACY/'Datos_analiticos_proyecto/validacion_temporal_20261028'
annual=pd.read_csv(out/'metricas_2026_completo.csv',dtype={'horizonte':str})
checks=[]
for h in range(1,6):
    result=get(f'/history?evaluation=updated&horizon={h}')
    assert result['data_version']=='evaluacion_local_20261028'
    for label,method in [('model','19_mensual_sin_clima'),('engineer','Ingeniero')]:
        expected=annual.loc[annual.horizonte.eq(str(h))&annual.metodo.eq(method)].iloc[0]
        assert result[label]['cases']==expected.casos
        assert np.isclose(result[label]['wape'],expected.WAPE) and np.isclose(result[label]['bias'],expected.sesgo_pct)
    checks.append({'horizon':h,'cases':result['model']['cases'],'matched':True})
comparison=get('/comparison?evaluation=updated&horizon=1')
weeks={r['label']:r for r in comparison['available_weeks']}
assert all(f'2026-S{n:02}' in weeks for n in [1,2,37,42,43])
no_pair=get('/comparison?evaluation=updated&horizon=1&weeks=2026-01-05')
assert no_pair['available_cases']>0 and no_pair['model']['cases']==0
assert no_pair['model_available']['wape'] is not None
training=get('/history?evaluation=train&horizon=1')
assert '2026-10-05' in training['evaluation_note']
report=json.loads((STORAGE/'verification_operational.json').read_text(encoding='utf-8'))
run=get('/forecasts/'+report['forecast_id'])
assert run['state']=='borrador' and run['metadata']['dataset_id']=='evaluacion_local_20261028'
proposal=pd.read_parquet(out/'pronostico_mas_reciente.parquet')
lines=pd.DataFrame(run['lines']).rename(columns={'product':'producto','variety':'variedad','horizon':'horizonte','target':'semana_objetivo'})
lines['finca']=run['farm'];lines['semana_objetivo']=pd.to_datetime(lines.semana_objetivo)
joined=proposal.merge(lines[KEY+['horizonte','semana_objetivo','model']],on=KEY+['horizonte','semana_objetivo'],validate='one_to_one')
assert len(joined)==len(proposal)==len(lines)
error=(joined.prediccion-joined.model).abs()
assert np.allclose(joined.prediccion,joined.model,rtol=0,atol=1e-6)
result={'passed':True,'api_matches_annual_metrics':checks,'weeks_S01_S02_S43_visible':True,
        'no_engineer_pair_does_not_invent_winner':True,'training_cutoff_visible':'2026-10-05',
        'forecast_id':run['id'],'forecast_rows':len(joined),'forecast_matches_notebook':True,
        'max_forecast_difference':float(error.max()),'not_published':True}
(STORAGE/'verification_updated_evaluation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
