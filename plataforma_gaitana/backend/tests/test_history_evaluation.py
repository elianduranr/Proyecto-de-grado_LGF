import pandas as pd
import pytest
from app import data
from app.history_eval import eligible_publications, engineer_archive
from pathlib import Path


def test_prospective_guard_excludes_backdated_and_unfinished():
    d = pd.DataFrame({
        'origen': ['2026-10-12']*3,
        'semana_objetivo': ['2026-10-12','2026-10-12','2026-10-26'],
        'published_at': ['2026-10-08','2026-10-20','2026-10-08'],
    })
    assert eligible_publications(d, '2026-10-26').index.tolist() == [0]


def test_history_modes_keep_comparable_cases_and_training_h1():
    training=data.history(evaluation='train')
    validation=data.history(evaluation='validation')
    test=data.history(evaluation='test')
    assert training['model']['cases'] > 0
    assert training['model']['cases'] == training['engineer']['cases']
    assert training['unmatched_cases'] > 0
    assert max(w['date'] for w in validation['test_weeks']) < '2026-01-01'
    assert min(w['date'] for w in test['test_weeks']) >= '2026-01-01'
    assert data.history(horizon=2,evaluation='train')['model']['cases'] == 0
    with pytest.raises(ValueError): data.history(evaluation='unknown')


def test_engineer_nominal_does_not_duplicate_fallback_or_adjusted_rows():
    base=dict(finca='GAITANA',producto='MINICARNATION',color='WHITE',variedad='A',
              origen_nominal=pd.Timestamp('2026-01-12'),origen_solicitado=pd.Timestamp('2026-01-12'),
              semana_inicio=pd.Timestamp('2026-01-12'),horizonte_nominal=1,
              en_h1_h5=True,es_ajustado=False,archivo_es_posterior=False,archivo_origen='nominal.xlsx',estimado=100)
    d=pd.DataFrame([base,dict(base,archivo_es_posterior=True,estimado=900),
                    dict(base,es_ajustado=True,estimado=500)])
    result=engineer_archive(Path('.'),lambda _:d,data.KEY)
    assert result.ingeniero.tolist()==[100]


def test_error_breakdown_conserves_absolute_error_without_cancelling(monkeypatch):
    rows=pd.DataFrame(dict(finca=['GAITANA']*2,producto=['MINICARNATION']*2,color=['WHITE','PINK'],
        variedad=['A','B'],origen=pd.to_datetime(['2026-01-12']*2),
        semana_objetivo=pd.to_datetime(['2026-01-12']*2),horizonte=[1,1],
        y=[100,100],Seleccion_pre2026=[200,0],ingeniero=[100,150]))
    monkeypatch.setattr(data,'history_frame',lambda *args,**kwargs:rows.copy())
    result=data.error_comparison(level='color')
    assert result['model']['bias']==0
    assert result['model']['wape']==100
    assert sum(row['model']['absolute'] for row in result['breakdown'])==200
    assert sum(row['model']['share'] for row in result['breakdown'])==100
    assert sum(row['engineer']['absolute'] for row in result['breakdown'])==50
    assert result['absolute_totals']['model']==200
    with pytest.raises(ValueError):data.error_comparison(start='2026-02-01',end='2026-01-01')


def test_real_breakdown_matches_preserved_test_and_filters():
    original=data.history()
    result=data.error_comparison(level='variedad')
    assert result['model']==original['model']
    assert result['engineer']==original['engineer']
    assert sum(r['cases'] for r in result['breakdown'])==original['model']['cases']
    assert sum(r['real'] for r in result['breakdown'])==original['model']['real']
    week=result['available_weeks'][0]['date']
    one=data.error_comparison(start=week,end=week,product='MINICARNATION',level='color')
    assert len(one['test_weeks'])==1
    assert all(r['identity']['producto']=='MINICARNATION' for r in one['breakdown'])


def test_discontinuous_week_selection_uses_same_cases_and_conserves_errors():
    full=data.error_comparison()
    weeks=[full['available_weeks'][0]['date'],full['available_weeks'][-1]['date']]
    selected=data.error_comparison(weeks=weeks,level='color')
    assert [w['date'] for w in selected['test_weeks']]==weeks
    assert selected['model']['cases']==selected['engineer']['cases']
    assert sum(r['cases'] for r in selected['breakdown'])==selected['model']['cases']
    assert sum(r['model']['absolute'] for r in selected['breakdown'])==pytest.approx(selected['absolute_totals']['model'])
    assert selected['available_weeks']==full['available_weeks']


def test_selected_h1_keeps_origin_and_rejects_non_monday():
    frame=pd.DataFrame({'origen':pd.to_datetime(['2026-10-19','2026-10-26'])})
    assert data.forecast_origin(frame)==(pd.Timestamp('2026-10-26'),pd.Timestamp('2026-10-26'))
    selected,default=data.forecast_origin(frame,'2026-10-19')
    assert selected==pd.Timestamp('2026-10-19') and default==pd.Timestamp('2026-10-26')
    # Una semana futura se consulta como tal; no se sustituye por la última disponible.
    assert data.forecast_origin(frame,'2026-11-02')[0]==pd.Timestamp('2026-11-02')
    with pytest.raises(ValueError):data.forecast_origin(frame,'2026-10-28')


def test_generation_checks_readiness_of_requested_origin(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app,db_session
    from app.security import identity
    checked=[]
    def state(origin):
        checked.append(origin)
        return {'ready':False,'generation_note':'No hay variables para esa H1.'}
    monkeypatch.setattr(data,'status',state)
    app.dependency_overrides[identity]=lambda:'ingeniero'
    app.dependency_overrides[db_session]=lambda:None
    try:
        response=TestClient(app).post('/api/forecasts',json={'origin':'2026-11-02','variant':'Sin_clima'})
        assert response.status_code==422
        assert checked==['2026-11-02']
        assert 'No hay variables' in response.json()['detail']
    finally:app.dependency_overrides.clear()


def test_week_winner_recalculates_with_color_filter(monkeypatch):
    rows=pd.DataFrame({'finca':['GAITANA']*2,'producto':['MINICARNATION']*2,'color':['WHITE','PINK'],
        'variedad':['A','B'],'origen':pd.to_datetime(['2026-01-12']*2),
        'semana_objetivo':pd.to_datetime(['2026-01-12']*2),'horizonte':[1,1],
        'y':[100,100],'Seleccion_pre2026':[110,200],'ingeniero':[150,100]})
    monkeypatch.setattr(data,'history_frame',lambda *args,**kwargs:rows.copy())
    white=data.error_comparison(color='WHITE')['available_weeks'][0]
    pink=data.error_comparison(color='PINK')['available_weeks'][0]
    assert white['winner']=='model' and white['model_wape']==10
    assert pink['winner']=='engineer' and pink['engineer_wape']==0


def test_updated_metrics_use_new_source_version_without_changing_predictions(tmp_path,monkeypatch):
    import json
    from app import config
    from app.history_eval import updated_frame
    storage=tmp_path/'storage';storage.mkdir()
    monkeypatch.setattr(config,'STORAGE',storage)
    out=tmp_path/'Datos_analiticos_proyecto/validacion_temporal_20261028';out.mkdir(parents=True)
    (out/'resumen_ejecucion.json').write_text(json.dumps({'snapshot':'one'}),encoding='utf-8')
    key={'finca':'GAITANA','producto':'MINICARNATION','color':'WHITE','variedad':'A'}
    dt=pd.Timestamp('2026-01-12')
    pred=pd.DataFrame([{**key,'origen':dt,'semana_objetivo':dt,'horizonte':1,'prediccion':120,
        'modelo':'19_mensual_sin_clima','y':999,'ingeniero':999}])
    pred.to_parquet(out/'predicciones_actualizadas.parquet',index=False)
    for name,real,engineer in [('one',100,100),('two',80,110)]:
        root=storage/'datasets'/name;folder=root/'Datos_analiticos_proyecto';base=folder/'modelo_con_proyecciones_teoricas';base.mkdir(parents=True)
        (root/'manifest.json').write_text(json.dumps({'id':name,'outputs':{'produccion_real_limpio':{'through':'2026-01-18'}}}),encoding='utf-8')
        pd.DataFrame([{**key,'semana_inicio':dt,'tallos_reales':real}]).to_parquet(base/'produccion_clima_semanal.parquet',index=False)
        pd.DataFrame([{**key,'origen_nominal':dt,'origen_solicitado':dt,'semana_inicio':dt,'horizonte_nominal':1,
            'en_h1_h5':True,'es_ajustado':False,'archivo_es_posterior':False,'archivo_origen':'estimado.xlsx',
            'estimado':engineer}]).to_parquet(folder/'estimados_semanales_limpio.parquet',index=False)
    first=updated_frame(data.read,tmp_path,data.KEY)
    assert first.y.iloc[0]==100 and first.ingeniero.iloc[0]==100
    (storage/'metrics_source.json').write_text(json.dumps({'root':'datasets/two'}),encoding='utf-8')
    second=updated_frame(data.read,tmp_path,data.KEY)
    assert second.attrs['source_version']=='two'
    assert second.Seleccion_pre2026.iloc[0]==first.Seleccion_pre2026.iloc[0]==120
    assert data.metrics(second,'Seleccion_pre2026')['wape']==50
    assert data.metrics(second,'ingeniero')['wape']==37.5
