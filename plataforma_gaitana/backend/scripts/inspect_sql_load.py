"""Diagnóstico de transporte SQL sin exponer la URL ni credenciales."""
from sqlalchemy import select,text
from app.db import engine,Session,Job,now

print({'dialect':engine.dialect.name,'driver':engine.dialect.driver,
       'fast_executemany':getattr(engine.dialect,'fast_executemany',None),
       'insertmanyvalues_without_returning':getattr(engine.dialect,'use_insertmanyvalues_wo_returning',None)},flush=True)
with Session() as db:
    job=db.scalar(select(Job).where(Job.kind=='etl',Job.state=='en_proceso'))
    print({'created':str(job.created_at),'updated':str(job.updated_at),'now':str(now()),'message':job.message} if job else {'active_job':False},flush=True)
with engine.connect() as connection:
    print(tuple(connection.execute(text("SELECT CAST(SERVERPROPERTY('ProductVersion') AS varchar(50)),compatibility_level FROM sys.databases WHERE name=DB_NAME()")).first()),flush=True)
