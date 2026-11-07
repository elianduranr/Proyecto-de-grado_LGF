"""Rebuild originals with resumable checkpoints, without activating unfinished data."""
import argparse
from app.etl import rebuild

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('snapshot_id')
    args = parser.parse_args()
    last = ['']
    def progress(value, message):
        if message != last[0]:
            print(f'{value}% {message}', flush=True)
            last[0] = message
    root, manifest = rebuild(args.snapshot_id, progress)
    print('Procesamiento terminado. Pendiente validación y activación:', root, flush=True)
