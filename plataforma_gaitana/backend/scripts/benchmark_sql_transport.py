"""Comparar transportes en tablas temporales; no altera las tablas del proyecto."""
import gzip,json,time
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq
import sqlalchemy as sa
from app.sql_bulk import compressed_insert
from app.config import STORAGE
from app.db import engine
from app.clean_tables import CLEAN_TABLES

def main():
    assert engine.dialect.name=='mssql'
    source=CLEAN_TABLES['produccion_real_limpio']
    file=STORAGE/'datasets/evaluacion_local_20261028/Datos_analiticos_proyecto/produccion_real_limpio.parquet'
    batch=next(pq.ParquetFile(file).iter_batches(batch_size=2000))
    records=[{**r,'dataset_id':'test_transport','row_number':i} for i,r in enumerate(batch.to_pylist())]
    report={}
    with engine.connect() as connection:
        transaction=connection.begin()
        try:
            for method in ['odbc','gzip_json']:
                table=sa.Table('#lgf_probe_'+method,sa.MetaData(),*(sa.Column(c.name,c.type) for c in source.c))
                table.create(connection)
                start=time.perf_counter()
                if method=='odbc':connection.execute(table.insert(),records)
                else:report['bytes_compressed']=compressed_insert(connection,table,records)
                report[method+'_seconds']=round(time.perf_counter()-start,4)
                saved=pd.DataFrame(connection.execute(sa.select(table).order_by(table.c.row_number)).mappings())
                expected=pd.DataFrame(records)[list(saved.columns)]
                pd.testing.assert_frame_equal(saved,expected,check_dtype=False,check_exact=False,rtol=1e-13,atol=1e-13)
                report[method+'_exact_rows']=len(saved)
            report['passed']=True
        finally:transaction.rollback()
    report['speedup']=report['odbc_seconds']/report['gzip_json_seconds']
    (STORAGE/'verification_sql_transport.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
