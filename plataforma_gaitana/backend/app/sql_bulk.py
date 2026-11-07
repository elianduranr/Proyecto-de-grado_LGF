"""Transporte comprimido hacia SQL Server; conserva esquema, filas y transacciones."""
import gzip
import json
import sqlalchemy as sa


def payload(records):
    text=json.dumps(records,ensure_ascii=False,allow_nan=False,separators=(',',':'),default=lambda value:value.isoformat())
    return gzip.compress(text.encode('utf-16-le'),compresslevel=1,mtime=0)


def compressed_insert(connection,table,records):
    quote=connection.dialect.identifier_preparer.quote
    columns=list(table.c)
    target=connection.dialect.identifier_preparer.format_table(table)
    names=','.join(quote(column.name) for column in columns)
    schema=','.join(f'{quote(c.name)} {c.type.compile(dialect=connection.dialect)} N\'$."{c.name}"\'' for c in columns)
    for column in columns:
        if isinstance(column.type,sa.String) and column.type.length:
            if any(isinstance(row.get(column.name),str) and len(row[column.name].encode('utf-16-le'))//2>column.type.length for row in records):
                raise ValueError(f'{table.name}.{column.name}: longitud incompatible; no se truncaron valores.')
    sql=f'INSERT INTO {target} ({names}) SELECT {names} FROM OPENJSON(CONVERT(nvarchar(max),DECOMPRESS(CAST(:payload AS varbinary(max))))) WITH ({schema})'
    packed=payload(records)
    connection.execute(sa.text(sql).bindparams(sa.bindparam('payload',type_=sa.LargeBinary)),{'payload':packed})
    return len(packed)


def insert_batch(connection,table,records):
    if connection.dialect.name=='mssql':
        supported=connection.info.get('lgf_compressed_json')
        if supported is None:
            supported=bool(connection.scalar(sa.text("SELECT CASE WHEN compatibility_level>=130 AND CAST(SERVERPROPERTY('ProductMajorVersion') AS int)>=13 THEN 1 ELSE 0 END FROM sys.databases WHERE name=DB_NAME()")))
            connection.info['lgf_compressed_json']=supported
        if supported:
            compressed_insert(connection,table,records)
            return
    connection.execute(table.insert(),records)
