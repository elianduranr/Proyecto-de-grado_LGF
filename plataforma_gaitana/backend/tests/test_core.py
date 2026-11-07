import io
import pytest
import pandas as pd
import openpyxl
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from app.adjustments import allocate
from app.data import metrics
from app.db import Base,Forecast,Line,Publication
from app.main import app,db_session
from app.security import identity

@pytest.fixture
def client(tmp_path,monkeypatch):
    engine=create_engine(f'sqlite:///{tmp_path / "test.db"}',connect_args={'check_same_thread':False}).execution_options(schema_translate_map={'EP':None})
    Base.metadata.create_all(engine);sessions=sessionmaker(engine,expire_on_commit=False)
    def session():
        with sessions() as db:yield db
    app.dependency_overrides[db_session]=session
    app.dependency_overrides[identity]=lambda:'ingeniero'
    import app.uploads as uploads
    monkeypatch.setattr(uploads,'STORAGE',tmp_path)
    with TestClient(app) as client:yield client,sessions
    app.dependency_overrides.clear();engine.dispose()

def seed(sessions):
    with sessions.begin() as db:
        run=Forecast(origin='2026-09-07',variant='Sin_clima',metadata_json={});db.add(run);db.flush()
        for var,m,v in [('ALFA',10.4,10),('BETA',20.6,21)]:
            db.add(Line(forecast_id=run.id,product='MINICARNATION',color='WHITE',variety=var,horizon=1,target='2026-09-07',model_value=m,final_value=v,theory=None,route='memoria_4_semanas'))
        return run.id

def test_largest_remainders_and_zero():
    assert allocate(10,[1,1,1])==[4,3,3]
    assert sum(allocate(1_234_567,[7,13,21,57]))==1_234_567
    assert allocate(0,[0,0])==[0,0]
    assert allocate(9,[0])==[9]
    with pytest.raises(ValueError):allocate(5,[0,0])
    with pytest.raises(ValueError):allocate(-1,[2])


def test_review_progress_persists_and_adjustment_reopens_only_affected_variety(client):
    http,sessions=client;run_id=seed(sessions)
    url=f'/api/forecasts/{run_id}/reviews'
    initial=http.get(url).json()
    assert initial['total']==initial['pending']==2
    identities=[{'product':'MINICARNATION','color':'WHITE','variety':v} for v in ['ALFA','BETA']]
    first=http.post(url,json={'expected_revision':0,'identities':identities}).json()
    assert first['percent']==100 and first['groups'][0]['complete']
    assert all(r['status']=='aceptada' for r in first['varieties'])
    assert http.get(url).json()['reviewed']==2
    stale=http.post(url,json={'expected_revision':0,'identities':identities})
    assert stale.status_code==409
    changed=http.post(f'/api/forecasts/{run_id}/adjustments',json={'expected_revision':1,'horizon':1,
        **identities[0],'total':15})
    assert changed.status_code==200,changed.text
    reopened=http.get(url).json()
    assert reopened['pending']==1 and not reopened['groups'][0]['complete']
    assert reopened['varieties'][0]['status']=='pendiente'
    assert reopened['varieties'][1]['status']=='aceptada'
    checked=http.post(url,json={'expected_revision':2,'identities':identities[:1]}).json()
    assert checked['varieties'][0]['status']=='ajustada' and checked['percent']==100
    pending=http.post(url,json={'expected_revision':3,'identities':identities[:1],'action':'pending'}).json()
    assert pending['pending']==1


def test_review_cannot_confirm_nonexistent_variety_or_published_run(client):
    http,sessions=client;run_id=seed(sessions)
    body={'expected_revision':0,'identities':[{'product':'MINICARNATION','color':'WHITE','variety':'NO_EXISTE'}]}
    assert http.post(f'/api/forecasts/{run_id}/reviews',json=body).status_code==422
    assert http.get(f'/api/forecasts/{run_id}').json()['revision']==0
    assert http.post(f'/api/forecasts/{run_id}/publish',json={'expected_revision':0}).status_code==200
    body['expected_revision']=1;body['identities'][0]['variety']='ALFA'
    assert http.post(f'/api/forecasts/{run_id}/reviews',json=body).status_code==409

def test_bias_and_wape_are_distinct():
    m=metrics(pd.DataFrame({'y':[100,100],'p':[80,120]}),'p')
    assert m['wape']==20 and m['bias']==0
    assert metrics(pd.DataFrame({'y':[0],'p':[10]}),'p')['wape'] is None


def test_curve_uses_existing_normalized_values_and_no_future_edition(tmp_path,monkeypatch):
    from app import data
    directory=tmp_path/'Notebooks/Proyecciones Teoricas Propias/resultados_todos_los_anios/2026'
    directory.mkdir(parents=True)
    rows=[{'clave_curva':'COMERCIAL|MINICARNATION|WHITE|ALFA','edad':age,
           'rendimiento_curva':value,'fecha_plano':pd.Timestamp(date)}
          for date,values in [('2026-09-07',[1.,3.,1.]),('2026-09-14',[9.,9.,9.])]
          for age,value in enumerate(values,10)]
    pd.DataFrame(rows).to_parquet(directory/'curvas.parquet',index=False)
    monkeypatch.setattr(data,'runtime_root',lambda:tmp_path)
    curve=data.curve('MINICARNATION','ALFA','WHITE','2026-09-07')
    assert curve['series']==[{'age':10,'yield':1.},{'age':11,'yield':3.},{'age':12,'yield':1.}]


def test_webflor_accepts_pending_climate_and_planes(client,monkeypatch):
    from app import webflor
    from app.db import Dataset,ActiveDataset,Upload,Job
    monkeypatch.setattr(webflor,'configured',lambda:True)
    http,sessions=client
    with sessions.begin() as db:
        db.add(Dataset(id='active',root='active',state='activo',manifest={}))
        db.add(ActiveDataset(id='vigente',dataset_id='active'))
        for source in ['clima','planos']:
            db.add(Upload(source=source,filename=source+'.xlsx',sha256=source[0]*64,
                mode='completo' if source=='clima' else 'adicional',state='pendiente_etl',report={'year':2026}))
    response=http.post('/api/data/webflor')
    assert response.status_code==202
    with sessions() as db:assert db.get(Job,response.json()['job_id']).kind=='webflor'


def test_webflor_explains_pending_complete_production(client,monkeypatch):
    from app import webflor
    from app.db import Dataset,ActiveDataset,Upload
    monkeypatch.setattr(webflor,'configured',lambda:True)
    http,sessions=client
    with sessions.begin() as db:
        db.add(Dataset(id='active',root='active',state='activo',manifest={}))
        db.add(ActiveDataset(id='vigente',dataset_id='active'))
        db.add(Upload(source='produccion',filename='2026.xlsx',sha256='p'*64,
            mode='completo',state='pendiente_etl',report={'year':2026}))
    response=http.post('/api/data/webflor')
    assert response.status_code==409
    assert 'completo de producción' in response.json()['detail']


def test_forecast_performance_recalculates_after_adjustment(client,monkeypatch,tmp_path):
    from app import data
    http,sessions=client
    run_id=seed(sessions)
    weekly=pd.DataFrame([{'finca':'GAITANA','producto':'MINICARNATION','color':'WHITE','variedad':v,
        'semana_inicio':pd.Timestamp('2026-09-07'),'tallos_reales':n} for v,n in [('ALFA',12),('BETA',18)]])
    monkeypatch.setattr(data,'weekly',lambda:weekly)
    monkeypatch.setattr(data,'runtime_paths',lambda:(tmp_path,tmp_path,tmp_path))
    monkeypatch.setattr(pd,'read_parquet',lambda *a,**kw:pd.DataFrame({'fecha_corte':[pd.Timestamp('2026-09-13')]}))
    first=http.get(f'/api/forecasts/{run_id}/performance').json()
    assert first['model']['cases']==first['adjusted']['cases']==2
    original=first['model']
    response=http.post(f'/api/forecasts/{run_id}/adjustments',json={'expected_revision':0,'horizon':1,
        'product':'MINICARNATION','color':'WHITE','variety':'ALFA','total':12,'note':'Control de actualización'})
    assert response.status_code==200,response.text
    second=http.get(f'/api/forecasts/{run_id}/performance').json()
    assert second['model']==original
    assert second['adjusted']['wape']<first['adjusted']['wape']

def test_adjustment_publication_and_conflict(client):
    http,sessions=client;rid=seed(sessions)
    with sessions() as db:assert db.scalar(select(Publication)) is None
    body={'expected_revision':0,'horizon':1,'product':'MINICARNATION','color':'WHITE','total':7}
    assert http.post(f'/api/forecasts/{rid}/adjustments',json=body).status_code==200
    saved=http.get(f'/api/forecasts/{rid}').json()
    assert sum(x['final'] for x in saved['lines'])==7
    assert [x['model'] for x in saved['lines']]==[10.4,20.6]
    assert http.post(f'/api/forecasts/{rid}/adjustments',json=body).status_code==409
    assert http.post(f'/api/forecasts/{rid}/publish',json={'expected_revision':1}).status_code==200
    assert http.post(f'/api/forecasts/{rid}/adjustments',json={**body,'expected_revision':2}).status_code==409
    new=seed(sessions)
    with sessions() as db:assert db.scalar(select(Publication)).forecast_id==rid
    assert http.post(f'/api/forecasts/{new}/publish',json={'expected_revision':0}).status_code==200
    assert http.get(f'/api/forecasts/{rid}').json()['state']=='reemplazado'

def test_viewer_and_negative_quantities(client):
    http,sessions=client;rid=seed(sessions)
    body={'expected_revision':0,'horizon':1,'product':'MINICARNATION','total':-1}
    assert http.post(f'/api/forecasts/{rid}/adjustments',json=body).status_code==422
    app.dependency_overrides[identity]=lambda:'consulta'
    assert http.post(f'/api/forecasts/{rid}/publish',json={'expected_revision':0}).status_code==403

def test_archive_does_not_activate_and_duplicate_is_idempotent(client):
    http,_=client
    workbook=openpyxl.Workbook();workbook.active.append(['Fecha','Tallos']);output=io.BytesIO();workbook.save(output)
    kwargs={'data':{'source':'produccion','mode':'adicional'},'files':{'file':('produccion.xlsx',output.getvalue(),'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}}
    one=http.post('/api/uploads',**kwargs);two=http.post('/api/uploads',**kwargs)
    assert one.status_code==two.status_code==200
    assert one.json()['state']=='pendiente_etl' and two.json()['duplicate']
    assert one.json()['id']==two.json()['id']
    bad=http.post('/api/uploads',data={'source':'clima','mode':'completo'},files={'file':('clima.xlsx',b'not excel')})
    assert bad.status_code==422


def test_excel_inspection_does_not_block_other_requests(client,monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    import app.uploads as uploads
    http,_=client;started=Event();release=Event()
    def inspect(_):
        started.set()
        assert release.wait(8)
        return [{'name':'BD','rows':1,'columns':1}]
    monkeypatch.setattr(uploads,'inspect_workbook',inspect)
    workbook=openpyxl.Workbook();output=io.BytesIO();workbook.save(output)
    with ThreadPoolExecutor(max_workers=2) as pool:
        request=pool.submit(http.post,'/api/uploads',data={'source':'clima','mode':'completo'},
            files={'file':('clima.xlsx',output.getvalue())})
        try:
            assert started.wait(3)
            assert pool.submit(http.get,'/api/health').result(timeout=2).status_code==200
        finally:release.set()
        assert request.result(timeout=3).status_code==200

def test_export_keeps_quantities_and_labels_preliminary(client):
    http,sessions=client;rid=seed(sessions)
    response=http.get(f'/api/forecasts/{rid}/export');assert response.status_code==200
    wb=openpyxl.load_workbook(io.BytesIO(response.content),data_only=True)
    assert wb.sheetnames==['Estimado','Trazabilidad','Información']
    assert 'prototipo' in str(list(wb['Información'].values)[1][-1]).lower()

def test_forecast_history_uses_same_series(client,monkeypatch):
    http,sessions=client;rid=seed(sessions)
    from app import data
    frame=pd.DataFrame([{'finca':'GAITANA','producto':'MINICARNATION','color':'WHITE','variedad':v,'semana_inicio':pd.Timestamp('2026-08-31'),'tallos_reales':n} for v,n in [('ALFA',100),('BETA',200),('GAMMA',900)]])
    monkeypatch.setattr(data,'weekly',lambda:frame)
    result=http.get('/api/series',params={'forecast_id':rid}).json()
    assert result[0]['tallos_reales']==300
