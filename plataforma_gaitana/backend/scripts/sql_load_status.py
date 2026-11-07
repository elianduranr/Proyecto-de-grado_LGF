"""Read-only diagnostics of this application's staging, not other applications."""
import json
from sqlalchemy import text
from app.db import engine


def main():
    with engine.connect() as conn:
        counts=conn.execute(text("SELECT t.name,SUM(p.row_count) AS rows FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id JOIN sys.dm_db_partition_stats p ON p.object_id=t.object_id AND p.index_id IN(0,1) WHERE s.name='EP' AND t.name LIKE 'lgf_%' GROUP BY t.name ORDER BY t.name")).mappings().all()
        requests=conn.execute(text("SELECT r.session_id,r.status,r.command,r.wait_type,r.wait_time,r.blocking_session_id,r.cpu_time,r.total_elapsed_time,LEFT(x.text,500) AS statement FROM sys.dm_exec_requests r CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) x WHERE r.database_id=DB_ID() AND r.session_id<>@@SPID AND (x.text LIKE '%[[]EP[]]%' OR x.text LIKE '%EP.lgf_%')")).mappings().all()
        versions=conn.execute(text('SELECT version_num FROM EP.lgf_alembic_version')).scalars().all()
    print(json.dumps({'rows_approximate':[dict(r) for r in counts],'requests':[dict(r) for r in requests], 'migrations':versions},indent=2,default=str),flush=True)


if __name__=='__main__':main()
