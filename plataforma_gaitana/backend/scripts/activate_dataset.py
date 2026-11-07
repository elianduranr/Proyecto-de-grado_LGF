"""Validate, persist and activate an already rebuilt private snapshot."""
import argparse
import json
from app.config import STORAGE
from app.etl_store import persist_and_activate

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('snapshot_id')
    args=parser.parse_args()
    if any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.snapshot_id):
        raise ValueError('Identificador no válido')
    root=STORAGE/'datasets'/args.snapshot_id
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    if manifest['id']!=args.snapshot_id or len(manifest['completed_stages'])!=11:
        raise ValueError('La cadena de procesamiento todavía no ha terminado.')
    persist_and_activate(root,manifest,progress=lambda value,message:print(f'{value}% {message}',flush=True))
    print('Base activada:',manifest['latest_origin'],flush=True)
