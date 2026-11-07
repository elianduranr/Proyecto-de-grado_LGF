"""Rebuild the canonical pipeline in private storage with checkpoints and source hashes."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import LEGACY, STORAGE

SOURCE_DIRS = {
    'produccion': 'Producción real', 'clima': 'Clima',
    'planos': 'Plano de Siembras', 'estadisticas': 'Curvas por variedad',
    'estimados': 'Estimados semanales',
}
CLEAN_DIR = 'Notebooks/Limpieza data, Notebooks y Scripts'
PROJECTION_DIR = 'Notebooks/Proyecciones Teoricas Propias'
MASTER_DIR = 'Notebooks/Extracción SQL/Datos/01_maestros_y_geografia'
STAGES = [
    (f'{CLEAN_DIR}/{i:02d}_{name}.ipynb', '-')
    for i, name in enumerate([
        'limpieza_curvas_variedad', 'limpieza_clima', 'limpieza_estimados_semanales',
        'limpieza_planos_siembra', 'limpieza_produccion_real',
    ], 1)
] + [
    (f'{PROJECTION_DIR}/00_catalogo_variedades.ipynb', '-'),
    (f'{PROJECTION_DIR}/Proyecciones_teoricas_todos_los_anios.ipynb', 'true'),
    (f'{PROJECTION_DIR}/Auditoria_calidad_curvas.ipynb', '-'),
    (f'{PROJECTION_DIR}/Proyecciones_teoricas_todos_los_anios.ipynb', 'false'),
    ('Notebooks/Analisis/10_base_analitica_proyecciones.ipynb', '-'),
    ('Notebooks/Modelo_de_series_diario/01_base_diaria_EDA.ipynb', '-'),
]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def save_json(path, document):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)


def prepare(snapshot_id, progress=lambda n, message: None):
    if not snapshot_id or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in snapshot_id):
        raise ValueError('Identificador de ejecución no válido.')
    workspace = STORAGE / 'datasets' / snapshot_id
    workspace.mkdir(parents=True, exist_ok=True)
    manifest_path = workspace / 'manifest.json'
    if manifest_path.exists():
        return workspace, json.loads(manifest_path.read_text(encoding='utf-8'))
    archive = STORAGE / 'source_archive'
    archive.mkdir(exist_ok=True)
    from .etl_sources import catalog, apply_uploads
    selected = catalog()
    raw = sorted(p for name in SOURCE_DIRS.values() for p in (LEGACY / 'Datos' / name).rglob('*.xlsx') if not p.name.startswith('~$'))
    if not raw:
        raise ValueError('No hay archivos originales en LEGACY_ROOT/Datos.')
    for i, original in enumerate(raw):
        before = original.stat()
        digest = sha256(original)
        frozen = archive / f'{digest}.xlsx'
        if not frozen.exists():
            temporary = archive / f'{digest}.{snapshot_id}.part'
            shutil.copyfile(original, temporary)
            if sha256(temporary) != digest:
                temporary.unlink(missing_ok=True)
                raise ValueError(f'El archivo cambió durante la copia: {original.name}')
            temporary.replace(frozen)
        if original.stat().st_mtime_ns != before.st_mtime_ns:
            raise ValueError(f'La fuente cambió durante la lectura: {original.name}')
        relative = original.relative_to(LEGACY)
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            # Independent copies: neither ETL nor a later source update can alter the archive.
            shutil.copyfile(frozen, destination)
        source = next(key for key, name in SOURCE_DIRS.items() if relative.parts[1] == name)
        old = selected.get(relative.as_posix())
        if not old or old.get('original_sha256') != digest:
            selected[relative.as_posix()] = {'source': source, 'path': relative.as_posix(), 'sha256': digest,
                    'original_sha256': digest, 'bytes': before.st_size, 'active': True}
        selected[relative.as_posix()]['original_mtime_ns'] = before.st_mtime_ns
        if i % 10 == 0:
            progress(int(8 * i / len(raw)), f'Archivando fuentes: {i + 1}/{len(raw)}')
    selected, uploads = apply_uploads(selected, SOURCE_DIRS)
    for row in selected.values():
        destination = workspace / row['path']
        if not row.get('active', True):
            destination.unlink(missing_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(archive / f'{row["sha256"]}.xlsx', destination)
    records = [r for r in selected.values() if r.get('active', True)]
    (workspace / 'Datos_analiticos_proyecto').mkdir(exist_ok=True)
    masters = workspace / MASTER_DIR
    masters.mkdir(parents=True, exist_ok=True)
    for name in ['TablasBasicas_Producto.csv', 'TablasBasicas_Color.csv', 'TablasBasicas_Variedad.csv']:
        shutil.copyfile(LEGACY / MASTER_DIR / name, masters / name)
    code = {}
    for relative in [*(r for r,_ in STAGES),'Notebooks/Analisis/19_modelos_clima_y_curvas_gaitana.ipynb']:
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(LEGACY / relative, destination)
        code[relative] = sha256(destination)
    manifest = {'id': snapshot_id, 'created_at': datetime.now(timezone.utc).isoformat(),
                'sources': records, 'catalog': list(selected.values()), 'uploads': uploads,
                'notebooks': code, 'completed_stages': [], 'state': 'preparado'}
    window_code=sha256(Path(__file__).with_name('production_windows.py'))
    executor_code=sha256(Path(__file__).with_name('etl_notebook.py'))
    manifest['production_window_reader_sha256']=hashlib.sha256(f'{window_code}:{executor_code}'.encode()).hexdigest()
    from .etl_reuse import reuse
    reuse(workspace,manifest,STAGES,MASTER_DIR,PROJECTION_DIR,sha256)
    save_json(manifest_path, manifest)
    return workspace, manifest


def rebuild(snapshot_id, progress=lambda n, message: None):
    workspace, manifest = prepare(snapshot_id, progress)
    manifest['state']='preparado'
    manifest['execution_policy']={'xml_readers':1,'xml_batches':True,
        'executor_sha256':sha256(Path(__file__).with_name('etl_notebook.py')),
        'xml_reader_sha256':sha256(Path(__file__).with_name('xml_estimates.py')),
        'note':'Original functions, decoding, final filter, file order and assertions preserved; bounded XML batches.'}
    save_json(workspace/'manifest.json',manifest)
    package_root = str(Path(__file__).resolve().parents[1])
    env = {**os.environ, 'PYTHONPATH': package_root, 'PYTHONIOENCODING': 'utf-8',
           'MPLBACKEND': 'Agg', 'OMP_NUM_THREADS': '2', 'OPENBLAS_NUM_THREADS': '2'}
    logs = workspace / 'logs'
    logs.mkdir(exist_ok=True)
    try:
        for index, (relative, rebuild_flag) in enumerate(STAGES):
            if index in manifest['completed_stages']:
                continue
            notebook = workspace / relative
            if sha256(notebook) != manifest['notebooks'][relative]:
                raise ValueError('El código congelado del ETL cambió; se requiere una nueva ejecución.')
            progress(10 + int(index * 65 / len(STAGES)), f'ETL {index + 1}/{len(STAGES)}: {notebook.stem}')
            with (logs / f'{index:02d}_{notebook.stem}.log').open('a', encoding='utf-8') as output:
                process = subprocess.Popen([sys.executable, '-u', '-m', 'app.etl_notebook', str(notebook), str(workspace), rebuild_flag],
                                           cwd=workspace, env=env, stdout=output, stderr=subprocess.STDOUT)
                while process.poll() is None:
                    time.sleep(3)
                    progress(10 + int(index * 65 / len(STAGES)), f'Procesando {notebook.stem}; detalle en el registro de ejecución')
                if process.returncode:
                    raise ValueError(f'Falló {notebook.stem}; consulta logs/{index:02d}_{notebook.stem}.log. Los datos vigentes no cambiaron.')
            manifest['completed_stages'].append(index)
            save_json(workspace / 'manifest.json', manifest)
        manifest['state'] = 'procesado'
        save_json(workspace / 'manifest.json', manifest)
        return workspace, manifest
    except Exception:
        manifest['state'] = 'error'
        save_json(workspace / 'manifest.json', manifest)
        raise
