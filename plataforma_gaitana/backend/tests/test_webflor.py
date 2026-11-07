"""Reconsulta, reemplazo por ventana y conservación de movimientos legítimos."""
import pandas as pd
import pytest
from app.webflor import compare_overlap, validate_report, MAPPING
from app.etl_append import unchanged_history


def fixture_report():
    row={column:None for column in MAPPING}
    row.update(Finca='GAITANA',Fecha=pd.Timestamp('2026-10-10'),Producto='Minicarnation',
               Color='Gold',Variedad='PIÑATA SUNDROPS',Tallos=10)
    return pd.DataFrame([row])


def test_report_overlap_uses_same_accents_and_rejects_changed_quantities():
    report=fixture_report()
    current=pd.DataFrame([{'finca':'GAITANA','fecha_corte':pd.Timestamp('2026-10-10'),
                          'producto':'MINICARNATION','color':'GOLD','variedad':'PINATA SUNDROPS','tallos':10}])
    assert compare_overlap(report,current).difference.eq(0).all()
    report.loc[0,'Tallos']=11
    with pytest.raises(ValueError,match='diferencias'):compare_overlap(report,current)


def test_current_day_and_invalid_quantities_cannot_be_imported():
    report=fixture_report()
    assert len(validate_report(report,'2026-10-01','2026-10-10'))==1
    with pytest.raises(ValueError,match='fuera'):validate_report(report,'2026-10-01','2026-10-09')
    report.loc[0,'Tallos']=None
    with pytest.raises(ValueError,match='cantidades'):validate_report(report,'2026-10-01','2026-10-10')


def test_append_proof_detects_historical_corrections_and_preserves_repeated_cuts(tmp_path):
    old=pd.DataFrame({'date':pd.to_datetime(['2026-10-09','2026-10-10','2026-10-10']), 'stems':[10,5,5]})
    new=pd.concat([pd.DataFrame({'date':pd.to_datetime(['2026-10-13']),'stems':[20]}),old],ignore_index=True)
    previous=tmp_path/'old.parquet';current=tmp_path/'new.parquet'
    old.to_parquet(previous,index=False);new.to_parquet(current,index=False)
    assert unchanged_history(previous,current,'date',pd.Timestamp('2026-10-10').to_pydatetime())
    new.loc[2,'stems']=6;new.to_parquet(current,index=False)
    assert not unchanged_history(previous,current,'date',pd.Timestamp('2026-10-10').to_pydatetime())


def test_window_replaces_complete_days_preserving_older_rows_and_repeated_cuts():
    from app.production_windows import filter_replaced_rows
    window={'path':'new.xlsx','sha256':'b','replace_window':{'start':'2026-10-10','end':'2026-10-12','received_at':'2026-10-13'}}
    old=pd.DataFrame({'FECHA CORTE':pd.to_datetime(['2026-10-09','2026-10-10','2026-10-11']), 'TALLOS':[5,10,20]})
    replacement=pd.DataFrame({'FECHA CORTE':pd.to_datetime(['2026-10-10']*2),'TALLOS':[7,7]})
    combined=pd.concat([filter_replaced_rows(old,'old.xlsx',[window]),filter_replaced_rows(replacement,'new.xlsx',[window])])
    assert combined.TALLOS.tolist()==[5,7,7]  # Día 11 retirado; corte repetido legítimo conservado.
    assert old.TALLOS.tolist()==[5,10,20]  # La fuente original no se modifica.
    later={'path':'later.xlsx','sha256':'c','replace_window':{'start':'2026-10-10','end':'2026-10-12','received_at':'2026-10-14'}}
    assert filter_replaced_rows(replacement,'new.xlsx',[window,later]).empty
    assert filter_replaced_rows(replacement,'later.xlsx',[window,later]).TALLOS.tolist()==[7,7]


def test_window_signature_detects_corrections_even_with_same_total_and_row_count():
    from app.webflor import window_changed
    report=fixture_report()
    current=pd.DataFrame([{'finca':'GAITANA','fecha_corte':pd.Timestamp('2026-10-10'),
        'producto':'MINICARNATION','color':'GOLD','variedad':'PINATA SUNDROPS','tallos':10}])
    assert not window_changed(report,current,'2026-10-01','2026-10-12')
    report['Lote']='OTRO LOTE'
    assert window_changed(report,current,'2026-10-01','2026-10-12')


def test_window_reader_filters_before_canonical_normalization(tmp_path):
    import json
    from app.production_windows import reader
    source=tmp_path/'old.xlsx';replacement=tmp_path/'new.xlsx'
    pd.DataFrame({'Fecha Corte':[46027,46028],'TALLOS':[1,2]}).to_excel(source,index=False)
    pd.DataFrame({'Fecha Corte':[46028],'TALLOS':[3]}).to_excel(replacement,index=False)
    manifest={'sources':[{'source':'produccion','path':'new.xlsx','sha256':'b',
        'replace_window':{'start':'2026-01-06','end':'2026-01-06','received_at':'2026-01-07'}}]}
    (tmp_path/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
    load=reader(tmp_path)
    with pd.ExcelFile(source,engine='calamine') as workbook:
        assert load(workbook).TALLOS.tolist()==[1]
    assert load(replacement).TALLOS.tolist()==[3]


def test_stage_accepts_corrections_and_other_pending_sources(tmp_path,monkeypatch):
    from datetime import date
    from sqlalchemy import create_engine,select
    from sqlalchemy.orm import sessionmaker
    from app import webflor
    from app.db import Base,Dataset,ActiveDataset,Upload
    engine=create_engine('sqlite://').execution_options(schema_translate_map={'EP':None})
    Base.metadata.create_all(engine);sessions=sessionmaker(engine,expire_on_commit=False)
    monkeypatch.setattr(webflor,'Session',sessions);monkeypatch.setattr(webflor,'STORAGE',tmp_path)
    folder=tmp_path/'current/Datos_analiticos_proyecto';folder.mkdir(parents=True)
    current=pd.DataFrame([{'finca':'GAITANA','fecha_corte':pd.Timestamp('2026-10-10'),
        'producto':'MINICARNATION','color':'GOLD','variedad':'PINATA SUNDROPS','tallos':10}])
    current.to_parquet(folder/'produccion_real_limpio.parquet',index=False)
    with sessions.begin() as db:
        db.add(Dataset(id='current',root='current',state='activo',manifest={}))
        db.add(ActiveDataset(id='vigente',dataset_id='current'))
        db.add(Upload(source='clima',filename='clima.xlsx',sha256='c'*64,mode='completo',state='pendiente_etl',report={'year':2026}))
    report=fixture_report();report['Tallos']=12
    class Cursor:
        description=[(c,) for c in report.columns]
        fetched=False
        def execute(self,*args):return self
        def fetchval(self):return date(2026,10,13)
        def fetchmany(self,n):
            if self.fetched:return []
            self.fetched=True
            return list(report.itertuples(index=False,name=None))
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def cursor(self):return Cursor()
        def rollback(self):pass
    monkeypatch.setattr(webflor,'connect',Connection)
    result=webflor.stage('ingeniero','refresh',lambda *_:None)
    assert result['requires_rebuild'] and result['new_rows']==0
    assert result['overlap_different']==1 and result['replacement_stems']==12
    with sessions() as db:
        received=db.scalar(select(Upload).where(Upload.source=='produccion'))
        assert received.report['replace_window']['end']=='2026-10-12'
        assert received.state=='pendiente_etl'
    assert pd.read_parquet(folder/'produccion_real_limpio.parquet').tallos.sum()==10
    engine.dispose()
