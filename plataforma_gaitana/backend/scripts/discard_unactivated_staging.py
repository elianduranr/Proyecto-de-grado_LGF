"""Remove only unreferenced SQL staging of a failed, never activated execution.

Original files, manifests, logs, jobs and audit remain available. Active and
historical source versions referenced by any dataset are explicitly protected.
"""
import argparse
from sqlalchemy import select,func,text
from app.db import Session,ActiveDataset,Dataset,DatasetSource,Forecast,Job,Audit
from app.clean_tables import CLEAN_TABLES


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset_id');args=parser.parse_args()
    target=args.dataset_id
    with Session() as db:
        dataset=db.get(Dataset,target)
        if not dataset:raise ValueError('No existe la ejecución indicada.')
        if dataset.state not in ['cargando','error','descartado'] or dataset.activated_at is not None:
            raise ValueError('La ejecución fue activada o no es un staging descartable.')
        if db.scalar(select(ActiveDataset).where(ActiveDataset.dataset_id==target)):
            raise ValueError('La ejecución está vigente.')
        if db.scalar(select(func.count()).select_from(DatasetSource).where(DatasetSource.source_dataset_id==target)):
            raise ValueError('Hay versiones que dependen de estos registros; no se eliminan.')
        if any(run.metadata_json.get('dataset_id')==target for run in db.scalars(select(Forecast))):
            raise ValueError('Existe un pronóstico que referencia la ejecución.')
        if any(job.payload.get('snapshot_id')==target for job in db.scalars(select(Job).where(Job.state.in_(['pendiente','en_proceso'])))):
            raise ValueError('La ejecución tiene un trabajo activo.')
    from app.db import engine
    if engine.dialect.name!='mssql':raise ValueError('Este mantenimiento está limitado al staging propio de EP en SQL Server.')
    removed={}
    for source,table in CLEAN_TABLES.items():
        total=0
        while True:
            with engine.begin() as conn:
                deleted=conn.execute(text(f'DELETE TOP (20000) FROM [EP].[{table.name}] WHERE dataset_id=:target'),{'target':target}).rowcount
            total+=deleted
            if deleted<20000:break
        removed[source]=total;print(source,total,flush=True)
        with engine.connect() as conn:
            if conn.scalar(select(func.count()).select_from(table).where(table.c.dataset_id==target)):
                raise RuntimeError('Quedan bloques de staging; no se marca la ejecución como descartada.')
    with Session.begin() as db:
        db.get(Dataset,target).state='descartado'
        db.add(Audit(actor='administrador',action='staging_no_activado_descartado',object_id=target,details={'rows_removed':removed,'originals_preserved':True}))
    print('Sólo se retiraron bloques SQL no activados y sin referencias; se conserva la trazabilidad.',flush=True)


if __name__=='__main__':main()
