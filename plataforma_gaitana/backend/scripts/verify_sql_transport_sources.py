"""Probar los cinco esquemas en tablas temporales y comparar todas sus columnas."""
import json,time
import pandas as pd
import pyarrow.parquet as pq
import sqlalchemy as sa
from app.sql_bulk import insert_batch
from app.db import engine
from app.config import STORAGE
from app.clean_tables import CLEAN_TABLES

report=[]
for index,(name,source) in enumerate(CLEAN_TABLES.items()):
    path=STORAGE/f'datasets/evaluacion_local_20261028/Datos_analiticos_proyecto/{name}.parquet'
    batch=next(pq.ParquetFile(path).iter_batches(batch_size=2000))
    records=[{**r,'dataset_id':'transport_probe','row_number':i} for i,r in enumerate(batch.to_pylist())]
    with engine.connect() as connection:
        transaction=connection.begin()
        try:
            table=sa.Table(f'#lgf_transport_{index}',sa.MetaData(),*(sa.Column(c.name,c.type) for c in source.c))
            table.create(connection);start=time.perf_counter();insert_batch(connection,table,records)
            seconds=time.perf_counter()-start
            saved=pd.DataFrame(connection.execute(sa.select(table).order_by(table.c.row_number)).mappings())
            pd.testing.assert_frame_equal(saved,pd.DataFrame(records)[list(saved.columns)],check_dtype=False,check_exact=False,rtol=1e-13,atol=1e-13)
            item={'source':name,'rows':len(saved),'columns':len(saved.columns),'matched':True,'seconds':round(seconds,3)}
            report.append(item);print(item,flush=True)
        finally:transaction.rollback()
(STORAGE/'verification_sql_transport_sources.json').write_text(json.dumps({'passed':True,'sources':report},indent=2),encoding='utf-8')
