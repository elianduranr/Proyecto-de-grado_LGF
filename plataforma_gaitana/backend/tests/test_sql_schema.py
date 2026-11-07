"""Check SQL Server DDL without needing credentials or modifying a database."""
import importlib.util
import io
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations


def test_orm_qualifies_tables_and_foreign_keys_in_ep(monkeypatch):
    from app import config
    monkeypatch.setattr(config, 'DATABASE_URL', 'mssql+pyodbc:///?driver=ODBC+Driver+18+for+SQL+Server')
    path = Path(__file__).resolve().parents[1] / 'app/db.py'
    spec = importlib.util.spec_from_file_location('app._schema_check', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        assert len(module.Base.metadata.tables) == 10
        for table in module.Base.metadata.tables.values():
            assert table.schema == 'EP'
            for foreign_key in table.foreign_keys:
                assert foreign_key.column.table.schema == 'EP'
    finally:
        module.engine.dispose()


def test_initial_migration_keeps_all_sql_objects_in_ep():
    output = io.StringIO()
    context = MigrationContext.configure(
        dialect_name='mssql', opts={'as_sql': True, 'output_buffer': output}
    )
    path = Path(__file__).resolve().parents[1] / 'migrations/versions/0001_prototype.py'
    spec = importlib.util.spec_from_file_location('initial_migration', path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    with Operations.context(context):
        migration.upgrade()
    sql = output.getvalue()
    assert sql.count('CREATE TABLE [EP].') == 6
    assert sql.count('REFERENCES [EP].lgf_forecasts (id)') == 2
    assert 'ON [EP].lgf_forecast_lines' in sql
    assert 'dbo.' not in sql


def test_initial_migration_still_supports_local_sqlite():
    from sqlalchemy import create_engine, inspect
    engine = create_engine('sqlite://')
    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        path = Path(__file__).resolve().parents[1] / 'migrations/versions/0001_prototype.py'
        spec = importlib.util.spec_from_file_location('sqlite_initial_migration', path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        with Operations.context(context):
            migration.upgrade()
        assert len(inspect(connection).get_table_names()) == 6
        assert inspect(connection).get_foreign_keys('lgf_forecast_lines')[0]['referred_table'] == 'lgf_forecasts'
    engine.dispose()


def test_etl_migrations_keep_normalized_sources_in_ep():
    output=io.StringIO()
    context=MigrationContext.configure(dialect_name='mssql',opts={'as_sql':True,'output_buffer':output})
    versions=Path(__file__).resolve().parents[1]/'migrations/versions'
    with Operations.context(context):
        for filename in ['0002_etl.py','0003_source_catalog.py','0004_dataset_sources.py']:
            spec=importlib.util.spec_from_file_location('schema_migration',versions/filename)
            migration=importlib.util.module_from_spec(spec);spec.loader.exec_module(migration)
            migration.upgrade()
    sql=output.getvalue()
    assert sql.count('CREATE TABLE [EP].')==9
    assert sql.count('REFERENCES [EP].lgf_datasets (id)')==9
    assert sql.count('CREATE VIEW [EP].')==5
    assert 'dbo.' not in sql
