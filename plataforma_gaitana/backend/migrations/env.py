from alembic import context
from app.db import engine, Base
from app.clean_tables import CLEAN_TABLES


def include_name(name, type_, parent_names):
    if type_ == 'schema':
        return name == 'EP' if is_sql_server else name is None
    if type_ == 'table':
        return name.startswith('lgf_')
    return True

is_sql_server = engine.dialect.name == 'mssql'
if is_sql_server:
    # Run before Alembic creates its own version table. Never use dbo implicitly.
    with engine.begin() as connection:
        connection.exec_driver_sql("IF SCHEMA_ID(N'EP') IS NULL EXEC(N'CREATE SCHEMA [EP]')")

with engine.connect() as connection:
    context.configure(connection=connection,target_metadata=Base.metadata,
        include_schemas=is_sql_server,
        include_name=include_name,
        version_table_schema='EP' if is_sql_server else None,
        version_table='lgf_alembic_version' if is_sql_server else 'alembic_version')
    with context.begin_transaction():context.run_migrations()
