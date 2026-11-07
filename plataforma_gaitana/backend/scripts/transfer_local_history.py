"""Copy prototype records to EP atomically, preserving IDs and the SQLite backup."""
from sqlalchemy import create_engine, select, func
from app.config import STORAGE
from app.db import Base, engine


def main():
    if engine.dialect.name != 'mssql':
        raise RuntimeError('Configure SQL Server antes de transferir el histórico.')
    source = STORAGE / 'prototipo.db'
    if not source.exists():
        raise RuntimeError('No existe el histórico local.')
    local = create_engine(f'sqlite:///{source.as_posix()}').execution_options(schema_translate_map={'EP': None})
    report = {}
    with local.connect() as original, engine.begin() as destination:
        for table in Base.metadata.sorted_tables:
            if table.name not in {'lgf_audit','lgf_forecasts','lgf_jobs','lgf_uploads','lgf_forecast_lines','lgf_publications'}:
                continue
            rows = original.execute(select(table)).mappings().all()
            existing = {row[0] for row in destination.execute(select(table.c.id))}
            missing = [dict(row) for row in rows if row['id'] not in existing]
            if missing:
                destination.execute(table.insert(), missing)
            remaining = set(row['id'] for row in rows) - set(destination.execute(select(table.c.id)).scalars())
            if remaining:
                raise RuntimeError(f'Transferencia incompleta: {table.name}')
            report[table.name] = {'local': len(rows), 'copiados': len(missing)}
    local.dispose()
    print(report)


if __name__ == '__main__':
    main()
