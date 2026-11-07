from datetime import datetime
import gzip,json
import pytest
import sqlalchemy as sa
from app.sql_bulk import payload,insert_batch,compressed_insert


def test_compressed_payload_preserves_unicode_null_boolean_datetime_and_numbers():
    rows=[{'name':'Clavel rosado · áéíóú 🌸','missing':None,'flag':False,'n':1234567890123,
           'f':.12345678901234567,'date':datetime(2026,10,27,13,15,2,123456)}]
    restored=json.loads(gzip.decompress(payload(rows)).decode('utf-16-le'))
    assert restored==[{**rows[0],'date':rows[0]['date'].isoformat()}]
    with pytest.raises(ValueError):payload([{'invalid':float('nan')}])


def test_sqlite_transport_uses_normal_insert():
    engine=sa.create_engine('sqlite://')
    table=sa.Table('sample',sa.MetaData(),sa.Column('n',sa.Integer),sa.Column('name',sa.Unicode(20)))
    with engine.begin() as connection:
        table.create(connection);insert_batch(connection,table,[{'n':1,'name':'Gaitana'}])
        assert connection.execute(sa.select(table)).all()==[(1,'Gaitana')]


def test_compressed_transport_does_not_truncate_long_strings():
    from sqlalchemy.dialects import mssql
    class Connection:
        dialect=mssql.dialect()
        def execute(self,*args,**kwargs):raise AssertionError('No debe escribir datos truncados.')
    table=sa.Table('sample',sa.MetaData(),sa.Column('name',sa.Unicode(3)))
    with pytest.raises(ValueError):compressed_insert(Connection(),table,[{'name':'largo'}])
