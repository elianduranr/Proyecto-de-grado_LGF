"""Queue a failed private workspace for the worker without downloading cuts again."""
import argparse
from sqlalchemy import select
from app.config import STORAGE
from app.db import Session,Dataset,Job,Audit


def main():
    parser=argparse.ArgumentParser();parser.add_argument('snapshot_id');args=parser.parse_args()
    snapshot=args.snapshot_id
    if not snapshot or any(character not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for character in snapshot):raise ValueError('Identificador no válido.')
    if not (STORAGE/'datasets'/snapshot).is_dir():raise ValueError('No existe la carpeta privada de la ejecución.')
    with Session.begin() as db:
        old=db.get(Dataset,snapshot)
        if old and old.state=='activo':raise ValueError('La ejecución ya está activa; no se modifica.')
        if db.scalar(select(Job).where(Job.state.in_(['pendiente','en_proceso']))):raise ValueError('Hay un trabajo activo; no se pone otro en cola.')
        job=Job(kind='etl',payload={'actor':'administrador','snapshot_id':snapshot});db.add(job);db.flush()
        db.add(Audit(actor='administrador',action='etl_reanudacion_solicitada',object_id=job.id,details={'snapshot_id':snapshot}))
        print(job.id,flush=True)


if __name__=='__main__':main()
