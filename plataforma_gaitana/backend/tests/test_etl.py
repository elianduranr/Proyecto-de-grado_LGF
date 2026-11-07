"""ETL activation must preserve the last valid dataset when a load fails."""
import copy
import pandas as pd
import pytest
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from app.db import Base, ActiveDataset,DatasetSource
from app.clean_tables import CLEAN_TABLES, SCHEMAS
from app import etl_store


def make_snapshot(root, stems=10):
    folder=root/'Datos_analiticos_proyecto';folder.mkdir(parents=True)
    date=pd.Timestamp('2026-01-05')
    for name, fields in SCHEMAS.items():
        row={f['name']:None for f in fields}
        row[etl_store.DATE_COLUMNS[name]]=date
        if name=='produccion_real_limpio':row.update(finca='GAITANA',tallos=stems,semana_inicio=date)
        pd.DataFrame([row]).to_parquet(folder/f'{name}.parquet',index=False)
    model=folder/'modelo_con_proyecciones_teoricas';model.mkdir()
    key={'finca':'GAITANA','producto':'TEST','color':'TEST','variedad':'TEST'}
    pd.DataFrame([{**key,'origen':date,'horizonte':1,'admisible_modelo':True}]).to_parquet(model/'base_analitica_proyecciones.parquet',index=False)
    pd.DataFrame([{**key,'semana_inicio':date,'tallos_reales':10}]).to_parquet(model/'produccion_clima_semanal.parquet',index=False)
    daily=folder/'modelo_diario';daily.mkdir()
    pd.DataFrame([{'fecha':date}]).to_parquet(daily/'features_diarias.parquet',index=False)
    return root


def test_bulk_activation_is_idempotent_and_bad_replacement_keeps_current(tmp_path,monkeypatch):
    engine=create_engine('sqlite://').execution_options(schema_translate_map={'EP':None})
    Base.metadata.create_all(engine)
    sessions=sessionmaker(engine,expire_on_commit=False)
    monkeypatch.setattr(etl_store,'engine',engine);monkeypatch.setattr(etl_store,'Session',sessions)
    monkeypatch.setattr(etl_store,'STORAGE',tmp_path)
    root=make_snapshot(tmp_path/'good')
    manifest={'id':'good','sources':[]}
    etl_store.persist_and_activate(root,manifest)
    etl_store.persist_and_activate(root,manifest)
    with sessions() as db:
        assert db.get(ActiveDataset,'vigente').dataset_id=='good'
        table=CLEAN_TABLES['produccion_real_limpio']
        assert db.scalar(select(func.count()).select_from(table))==1
    another=make_snapshot(tmp_path/'next')
    etl_store.persist_and_activate(another,{'id':'next','sources':[]})
    with sessions() as db:
        assert db.get(ActiveDataset,'vigente').dataset_id=='next'
        assert db.get(DatasetSource,('next','produccion_real_limpio')).source_dataset_id=='good'
        assert db.scalar(select(func.count()).select_from(table))==1
    bad=make_snapshot(tmp_path/'bad',stems=11)
    with pytest.raises(ValueError,match='no conserva los tallos'):
        etl_store.persist_and_activate(bad,{'id':'bad','sources':[]})
    with sessions() as db:
        assert db.get(ActiveDataset,'vigente').dataset_id=='next'
        assert db.scalar(select(func.count()).select_from(table))==1
    engine.dispose()


def test_incremental_dates_do_not_interpret_excel_serial_as_1970(tmp_path):
    from app.etl_sources import additional_dates
    workbook=tmp_path/'incremental.xlsx'
    pd.DataFrame({'FECHA CORTE':[46027]}).to_excel(workbook,sheet_name='BD',index=False)
    assert additional_dates(workbook,'produccion').iloc[0]==pd.Timestamp('2026-01-05')


def test_complete_batch_allows_different_families_but_rejects_competing_replacements():
    from app.etl_sources import validate_batch
    def upload(name,source='estadisticas',mode='completo'):
        return {'filename':name,'source':source,'mode':mode,'report':{'year':2026}}
    validate_batch([upload('Clavel 2026.xlsx'),upload('Mini Clavel 2026.xlsx')])
    with pytest.raises(ValueError,match='varios archivos completos'):
        validate_batch([upload('Clavel 2026.xlsx'),upload('Clavel nuevo 2026.xlsx')])
    with pytest.raises(ValueError,match='Procese primero'):
        validate_batch([upload('2026.xlsx','produccion'),upload('adicional 2026.xlsx','produccion','adicional')])


def test_corrected_history_creates_new_sql_version_without_changing_previous(tmp_path,monkeypatch):
    engine=create_engine('sqlite://').execution_options(schema_translate_map={'EP':None})
    Base.metadata.create_all(engine);sessions=sessionmaker(engine,expire_on_commit=False)
    monkeypatch.setattr(etl_store,'engine',engine);monkeypatch.setattr(etl_store,'Session',sessions)
    monkeypatch.setattr(etl_store,'STORAGE',tmp_path)
    etl_store.persist_and_activate(make_snapshot(tmp_path/'before'),{'id':'before','sources':[]})
    corrected=make_snapshot(tmp_path/'corrected',stems=12)
    path=corrected/'Datos_analiticos_proyecto/modelo_con_proyecciones_teoricas/produccion_clima_semanal.parquet'
    weekly=pd.read_parquet(path);weekly['tallos_reales']=12;weekly.to_parquet(path,index=False)
    etl_store.persist_and_activate(corrected,{'id':'corrected','sources':[]})
    table=CLEAN_TABLES['produccion_real_limpio']
    with sessions() as db:
        assert db.get(ActiveDataset,'vigente').dataset_id=='corrected'
        assert db.get(DatasetSource,('before','produccion_real_limpio')).source_dataset_id=='before'
        assert db.get(DatasetSource,('corrected','produccion_real_limpio')).source_dataset_id=='corrected'
        assert db.scalar(select(table.c.tallos).where(table.c.dataset_id=='before'))==10
        assert db.scalar(select(table.c.tallos).where(table.c.dataset_id=='corrected'))==12
    engine.dispose()


def test_incremental_production_reuses_old_rows_and_versions_keep_their_limits(tmp_path,monkeypatch):
    engine=create_engine('sqlite://').execution_options(schema_translate_map={'EP':None})
    Base.metadata.create_all(engine);sessions=sessionmaker(engine,expire_on_commit=False)
    monkeypatch.setattr(etl_store,'engine',engine);monkeypatch.setattr(etl_store,'Session',sessions)
    monkeypatch.setattr(etl_store,'STORAGE',tmp_path)
    previous=make_snapshot(tmp_path/'old')
    etl_store.persist_and_activate(previous,{'id':'old','sources':[]})
    current=make_snapshot(tmp_path/'updated')
    folder=current/'Datos_analiticos_proyecto'
    path=folder/'produccion_real_limpio.parquet'
    original=pd.read_parquet(path);additional=original.copy()
    additional['fecha_corte']=pd.Timestamp('2026-01-12');additional['semana_inicio']=pd.Timestamp('2026-01-12')
    pd.concat([additional,original],ignore_index=True).to_parquet(path,index=False)
    weekly=folder/'modelo_con_proyecciones_teoricas/produccion_clima_semanal.parquet'
    values=pd.read_parquet(weekly);values['tallos_reales']=20;values.to_parquet(weekly,index=False)
    etl_store.persist_and_activate(current,{'id':'updated','sources':[]})
    table=CLEAN_TABLES['produccion_real_limpio']
    with sessions() as db:
        before=db.get(DatasetSource,('old','produccion_real_limpio'))
        after=db.get(DatasetSource,('updated','produccion_real_limpio'))
        assert before.source_dataset_id==after.source_dataset_id=='old'
        assert (before.rows,after.rows)==(1,2)
        assert db.scalar(select(func.count()).select_from(table))==2
        assert db.scalar(select(func.count()).select_from(table).where(table.c.dataset_id=='old',table.c.row_number<before.rows))==1
        assert db.get(ActiveDataset,'vigente').dataset_id=='updated'
    engine.dispose()
