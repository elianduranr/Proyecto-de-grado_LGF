"""Source selection rules; changing a draft inventory never changes the active data."""
import re
import shutil
from pathlib import Path
import pandas as pd
from sqlalchemy import select
from .config import STORAGE
from .db import Session, SourceFile, Upload, ActiveDataset, Dataset


def catalog():
    with Session() as db:
        pointer=db.get(ActiveDataset,'vigente')
        active=db.get(Dataset,pointer.dataset_id) if pointer else None
        prior={r['path']:r for r in active.manifest.get('catalog',[]) } if active else {}
        return {r.path: {'path': r.path, 'source': r.source, 'sha256': r.sha256,
                        'original_sha256': r.original_sha256, 'bytes': r.size, 'active': bool(r.active)}
                        | {'display_name':prior.get(r.path,{}).get('display_name',Path(r.path).name)}
                        | ({'replace_window':prior[r.path]['replace_window']} if prior.get(r.path,{}).get('replace_window') else {})
                for r in db.scalars(select(SourceFile))}


def year_of(path):
    years = re.findall(r'20\d{2}', str(path))
    if not years:
        raise ValueError(f'No se reconoce el año de {path}.')
    return int(years[0])


def family(path):
    name = str(path).lower().replace(' ', '')
    if 'mini' in name and 'clavel' in name: return 'mini'
    if 'clavel' in name: return 'clavel'
    if 'green' in name and 'ball' in name: return 'greenball'
    if any(v in name for v in ['raffine', 'solomio', 'otros']): return 'otros'
    raise ValueError('El archivo de estadísticas debe identificar su familia: Clavel, Mini Clavel, Green Ball o Raffine/Solomio/Otros.')


def pending_uploads():
    with Session() as db:
        return [{'id': r.id, 'source': r.source, 'filename': r.filename, 'sha256': r.sha256,
                 'mode': r.mode, 'report': r.report} for r in db.scalars(
                     select(Upload).where(Upload.state == 'pendiente_etl').order_by(Upload.created_at))]


def additional_dates(path, source):
    date_column = 'FECHA CORTE' if source == 'produccion' else 'DATE'
    with pd.ExcelFile(path, engine='calamine') as workbook:
        if 'BD' not in workbook.sheet_names:
            raise ValueError('La carga adicional debe conservar la hoja BD y los encabezados del archivo original.')
        data = pd.read_excel(workbook, sheet_name='BD', usecols=lambda c: str(c).strip().upper() == date_column)
    if data.empty or len(data.columns) != 1:
        raise ValueError(f'No se encontró {date_column} en la carga adicional.')
    series = data.iloc[:, 0].dropna()
    dates = pd.to_datetime(series, format='mixed', errors='coerce')
    numeric = pd.to_numeric(series.astype('string'), errors='coerce')
    serial = numeric.between(20000, 80000)
    dates.loc[serial] = pd.to_datetime(numeric.loc[serial], unit='D', origin='1899-12-30')
    if dates.isna().any():
        raise ValueError('Hay fechas no válidas en la carga adicional.')
    return dates


def apply_uploads(records, source_dirs):
    applied = []
    uploads=pending_uploads()
    validate_batch(uploads)
    incremental={}
    for upload in uploads:
        source, year = upload['source'], int(upload['report']['year'])
        candidates = [r for r in records.values() if r.get('active', True) and r['source'] == source and year_of(r['path']) == year]
        name = upload['filename']
        root = f'Datos/{source_dirs[source]}'
        relative = f'{root}/{year}/{name}' if source in ['planos', 'estadisticas', 'estimados'] else f'{root}/{name}'
        if source=='produccion' and upload['report'].get('replace_window'):
            relative=f'{root}/{year}_webflor_{upload["id"]}.xlsx'
        elif source == 'planos':
            match = re.search(r'(?:semana|sem)\s*(\d+)', name, re.I)
            if not match: raise ValueError('El nombre del plano debe indicar Sem o Semana y su número.')
            week = int(match.group(1))
            same = [r for r in candidates if (m := re.search(r'(?:semana|sem)\s*(\d+)', Path(r['path']).stem, re.I)) and int(m.group(1)) == week]
            if same:
                if any(r['sha256'] == upload['sha256'] for r in same):
                    applied.append(upload['id']); continue
                raise ValueError(f'El plano de {year}, semana {week}, ya existe. Planos permite añadir semanas faltantes; no reemplazar una edición sin revisión.')
        elif source in ['clima', 'produccion'] and upload['mode'] == 'adicional':
            if str(year) not in name:
                relative = f'{root}/{year}_{name}'
            with Session() as db:
                active = db.get(ActiveDataset, 'vigente')
                if not active: raise ValueError('Procese primero los archivos existentes antes de añadir registros incrementales.')
                latest = db.get(Dataset, active.dataset_id)
                through = latest.manifest['outputs']['produccion_real_limpio' if source == 'produccion' else 'clima_limpio']['through']
            dates = additional_dates(STORAGE / 'uploads' / f'{upload["sha256"]}.xlsx', source)
            if dates.min().normalize() <= pd.Timestamp(through):
                raise ValueError(f'La carga adicional se cruza con fechas ya procesadas (hasta {through}). Use archivo completo para corregir o completar esas fechas; no se eliminarán movimientos de corte por coincidir sus valores.')
            if not dates.dt.year.eq(year).all():
                raise ValueError('El año seleccionado no coincide con las fechas del archivo adicional.')
            seen=incremental.setdefault((source,year),set())
            incoming=set(dates.dt.normalize())
            if seen & incoming:raise ValueError('Los archivos adicionales seleccionados comparten fechas. Separe períodos sin cruces; no se descartarán movimientos repetidos automáticamente.')
            seen.update(incoming)
            relative = f'{root}/{year}_adicional_{upload["id"]}.xlsx'
        elif source in ['clima', 'produccion', 'estadisticas']:
            if source == 'estadisticas':
                kind = family(name)
                candidates = [r for r in candidates if family(r['path']) == kind]
            if candidates:
                relative = candidates[0]['path']
            for row in candidates: row['active'] = False
        # A periodic engineer file replaces only the same named edition; never other weeks.
        if source in ['clima', 'produccion'] and str(year) not in Path(relative).name:
            relative = f'{root}/{year}_{Path(relative).name}'
        original_hash = records.get(relative, {}).get('original_sha256')
        frozen = STORAGE / 'source_archive' / f'{upload["sha256"]}.xlsx'
        if not frozen.exists():
            shutil.copyfile(STORAGE / 'uploads' / f'{upload["sha256"]}.xlsx', frozen)
        records[relative] = {'source': source, 'path': relative, 'sha256': upload['sha256'],
                             'original_sha256': original_hash, 'active': True, 'bytes': frozen.stat().st_size,'display_name':name}
        if upload['report'].get('replace_window'):
            records[relative]['replace_window']=upload['report']['replace_window']
        applied.append(upload['id'])
    return records, applied


def validate_batch(uploads):
    """No permitir que dos cargas completas del mismo alcance se borren entre sí."""
    scopes=set()
    for upload in uploads:
        source=upload['source'];year=int(upload['report']['year'])
        if source=='estadisticas':scope=(source,year,family(upload['filename']))
        elif source in ['produccion','clima'] and not upload['report'].get('replace_window'):
            scope=(source,year,'completo') if upload['mode']=='completo' else None
        else:scope=None
        if scope and scope in scopes:
            raise ValueError('Hay varios archivos completos para la misma fuente, año y familia. Cargue un único archivo completo por alcance; las familias distintas sí se pueden cargar juntas.')
        if scope:scopes.add(scope)
    for source,year,_ in scopes:
        if source in ['produccion','clima'] and any(u['source']==source and int(u['report']['year'])==year and
                (u['mode']=='adicional' or u['report'].get('replace_window')) for u in uploads):
            raise ValueError('Procese primero el archivo completo antes de combinarlo con adicionales o una actualización WebFlor del mismo año.')
