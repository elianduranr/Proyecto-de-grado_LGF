"""Persist normalized rows, then activate one fully validated dataset atomically."""
import json
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq
import pyarrow.compute as pc
from sqlalchemy import select, func

from .clean_tables import CLEAN_TABLES,SCHEMAS,TEXT_LENGTH
from .db import ActiveDataset, Audit, Dataset, DatasetSource, SourceFile, Upload, Session, engine, now
from .etl import sha256, save_json
from .config import LEGACY,STORAGE
from .sql_bulk import insert_batch

DATE_COLUMNS = {'produccion_real_limpio': 'fecha_corte', 'clima_limpio': 'fecha',
                'planos_siembra_limpio': 'semana_inicio', 'curvas_variedad_limpio': 'semana_inicio',
                'estimados_semanales_limpio': 'semana_inicio'}


def validate(workspace, manifest):
    folder = workspace / 'Datos_analiticos_proyecto'
    outputs = {}
    for name, table in CLEAN_TABLES.items():
        path = folder / f'{name}.parquet'
        parquet = pq.ParquetFile(path)
        expected = set(table.c.keys()) - {'dataset_id', 'row_number'}
        if set(parquet.schema_arrow.names) != expected or not parquet.metadata.num_rows:
            raise ValueError(f'Estructura o contenido no válidos: {name}')
        dates = pd.read_parquet(path, columns=[DATE_COLUMNS[name]])[DATE_COLUMNS[name]].dropna()
        text_columns=[field['name'] for field in SCHEMAS[name] if field['type']=='text']
        for batch in parquet.iter_batches(batch_size=100000,columns=text_columns):
            for column,values in zip(text_columns,batch.columns):
                if str(values.type)=='null':continue
                long=pc.filter(values,pc.greater(pc.utf8_length(values),TEXT_LENGTH//2))
                if any(len(value.encode('utf-16-le'))//2>TEXT_LENGTH for value in long.to_pylist() if value is not None):
                    raise ValueError(f'{name}.{column} excede {TEXT_LENGTH} unidades UTF-16; se requiere ampliar la columna SQL. No se truncaron datos.')
        outputs[name] = {'rows': parquet.metadata.num_rows, 'sha256': sha256(path),
                         'through': str(dates.max().date()), 'since': str(dates.min().date())}
    base = pd.read_parquet(folder / 'modelo_con_proyecciones_teoricas/base_analitica_proyecciones.parquet')
    key = ['finca', 'producto', 'color', 'variedad', 'origen', 'horizonte']
    if base.duplicated(key).any() or not base.horizonte.between(1, 5).all():
        raise ValueError('Casos repetidos o fuera de H1–H5 en la base analítica.')
    if not base.loc[base.origen.eq(base.origen.max()), 'admisible_modelo'].any():
        raise ValueError('El último origen no tiene historia suficiente para pronosticar.')
    weekly = pd.read_parquet(folder / 'modelo_con_proyecciones_teoricas/produccion_clima_semanal.parquet')
    actual = pd.read_parquet(folder / 'produccion_real_limpio.parquet', columns=['finca', 'tallos', 'semana_inicio'])
    expected_stems = actual.loc[actual.finca.eq('GAITANA') & actual.semana_inicio.ge('2021-01-01'), 'tallos'].sum()
    if weekly.tallos_reales.sum() != expected_stems:
        raise ValueError('La agregación semanal no conserva los tallos de la producción real.')
    pd.read_parquet(folder / 'modelo_diario/features_diarias.parquet', columns=['fecha'])
    manifest['outputs'] = outputs
    model_reference=workspace/'Notebooks/Analisis/19_modelos_clima_y_curvas_gaitana.ipynb'
    if model_reference.exists():
        manifest.setdefault('notebooks',{})['Notebooks/Analisis/19_modelos_clima_y_curvas_gaitana.ipynb']=sha256(model_reference)
    # Capture original file metadata only after verifying it still matches the frozen copy.
    for source in manifest.get('catalog',manifest['sources']):
        original=LEGACY/source['path']
        if original.exists() and not source.get('original_mtime_ns'):
            expected=source.get('original_sha256',source['sha256'])
            if expected and sha256(original)==expected:
                source['original_mtime_ns']=original.stat().st_mtime_ns
    manifest['latest_origin'] = str(base.origen.max().date())
    manifest['state'] = 'validado'
    save_json(workspace / 'manifest.json', manifest)
    return outputs


def persist_and_activate(workspace, manifest, actor='administrador', progress=lambda n, message: None):
    with Session() as db:
        existing=db.get(Dataset,manifest['id'])
        if existing and existing.state=='activo':
            for name,output in existing.manifest['outputs'].items():
                if sha256(workspace/'Datos_analiticos_proyecto'/f'{name}.parquet')!=output['sha256']:
                    raise ValueError('No se puede modificar una ejecución activada; cree una nueva versión.')
            return existing.manifest
    outputs = validate(workspace, manifest)
    dataset_id = manifest['id']
    with Session.begin() as db:
        row = db.get(Dataset, dataset_id)
        if row and row.state == 'activo':
            return manifest
        if row and row.manifest.get('outputs'):
            for source,item in outputs.items():
                if row.manifest['outputs'].get(source,{}).get('sha256')!=item['sha256']:
                    raise ValueError('La copia cambió después de comenzar su carga SQL; requiere otra versión antes de reanudar.')
        if not row:
            db.add(Dataset(id=dataset_id, state='cargando', root=workspace.relative_to(STORAGE).as_posix(), manifest=manifest))
        pointer=db.get(ActiveDataset,'vigente')
        previous=db.get(Dataset,pointer.dataset_id) if pointer else None
        previous_outputs=previous.manifest['outputs'] if previous else {}
        previous_id=previous.id if previous else None
        previous_root=Path(previous.root) if previous else None
        if previous_root is not None and not previous_root.is_absolute():previous_root=STORAGE/previous_root
    for index, (name, table) in enumerate(CLEAN_TABLES.items()):
        path = workspace / 'Datos_analiticos_proyecto' / f'{name}.parquet'
        if sha256(path) != outputs[name]['sha256']:
            raise ValueError(f'El archivo validado cambió: {name}')
        old=previous_outputs.get(name,{})
        owner=old.get('sql_dataset_id',previous_id) if old.get('sha256')==outputs[name]['sha256'] else dataset_id
        append=False
        if name=='produccion_real_limpio' and old and outputs[name]['rows']>old['rows'] and owner==dataset_id:
            from .etl_append import unchanged_history
            old_owner=old.get('sql_dataset_id',previous_id)
            with Session() as db:
                draft=db.get(DatasetSource,(dataset_id,name))
                resumable=bool(draft and draft.source_dataset_id==old_owner and draft.sha256==outputs[name]['sha256'])
            with engine.connect() as connection:
                physical=connection.scalar(select(func.count()).select_from(table).where(table.c.dataset_id==old_owner))
            if physical==old['rows'] or (resumable and old['rows']<=physical<=outputs[name]['rows']):
                progress(77,'Comprobando que los cortes históricos no cambiaron antes de añadir sólo las fechas nuevas a SQL')
                if unchanged_history(previous_root/'Datos_analiticos_proyecto'/f'{name}.parquet',path,'fecha_corte',pd.Timestamp(old['through']).to_pydatetime()):
                    owner=old_owner;append=True
                    with Session.begin() as db:
                        draft=db.get(DatasetSource,(dataset_id,name))
                        if not draft:db.add(DatasetSource(dataset_id=dataset_id,source_name=name,source_dataset_id=owner,rows=outputs[name]['rows'],sha256=outputs[name]['sha256']))
        outputs[name]['sql_dataset_id']=owner
        with engine.connect() as connection:
            stored = connection.scalar(select(func.count()).select_from(table).where(table.c.dataset_id == owner))
        if owner!=dataset_id and not append:
            if stored<outputs[name]['rows']:raise ValueError(f'La versión reutilizada de {name} no conserva su conteo SQL.')
            progress(77+index*4,f'SQL EP: {name} sin cambios; se reutiliza su versión validada')
            continue
        if owner==dataset_id and stored==outputs[name]['rows']:
            progress(77+index*4,f'SQL EP: {name} ya guardado; se conserva su carga verificada')
            continue
        offset = old['rows'] if append else 0
        if append:
            from .etl_append import blocks
            batches=blocks(path,'fecha_corte',pd.Timestamp(old['through']).to_pydatetime(),newer=True,size=2000)
        else:batches=pq.ParquetFile(path).iter_batches(batch_size=10000 if engine.dialect.name=='mssql' else 2000)
        for batch in batches:
            rows = batch.to_pylist()
            if offset + len(rows) <= stored:
                offset += len(rows)
                continue
            records = [{**r, 'dataset_id': owner, 'row_number': offset + i}
                       for i, r in enumerate(rows) if offset + i >= stored]
            with engine.begin() as connection:
                insert_batch(connection,table,records)
            offset += len(rows)
            if offset % 100_000 < 2000:
                progress(77 + index * 4, f'SQL EP: {name}, {offset:,}/{outputs[name]["rows"]:,} registros')
        with engine.connect() as connection:
            count = connection.scalar(select(func.count()).select_from(table).where(table.c.dataset_id == owner))
        if count != outputs[name]['rows']:
            raise ValueError(f'Conteo SQL no coincide: {name}')
    progress(98, 'Activando la base validada y su trazabilidad')
    with Session.begin() as db:
        pointer = db.get(ActiveDataset, 'vigente')
        if pointer:
            previous = db.get(Dataset, pointer.dataset_id)
            previous.state = 'reemplazado'
            pointer.dataset_id = dataset_id
        else:
            db.add(ActiveDataset(id='vigente', dataset_id=dataset_id))
        row = db.get(Dataset, dataset_id)
        row.state = 'activo'
        row.activated_at = now()
        row.manifest = {**manifest,'state':'activo'}
        for name,output in outputs.items():
            binding=db.get(DatasetSource,(dataset_id,name))
            if not binding:
                binding=DatasetSource(dataset_id=dataset_id,source_name=name);db.add(binding)
            binding.source_dataset_id=output['sql_dataset_id'];binding.rows=output['rows'];binding.sha256=output['sha256']
        for source in manifest.get('catalog', manifest['sources']):
            record=db.get(SourceFile,source['path'])
            if not record:
                record=SourceFile(path=source['path']);db.add(record)
            record.source=source['source'];record.sha256=source['sha256']
            record.original_sha256=source.get('original_sha256',source['sha256'])
            record.active=int(source.get('active',True));record.size=source['bytes'];record.dataset_id=dataset_id
        for receipt_id in manifest.get('uploads',[]):
            receipt=db.get(Upload,receipt_id)
            receipt.state='procesado'
            receipt.report={**receipt.report,'dataset_id':dataset_id,'message':'ETL validado y activado; datos limpios guardados en SQL.'}
        db.add(Audit(actor=actor, action='etl_activado', object_id=dataset_id,
                     details={'fuentes': len(manifest['sources']), 'outputs': outputs}))
    manifest['state'] = 'activo'
    save_json(workspace / 'manifest.json', manifest)
    save_json(STORAGE/'metrics_source.json',{'dataset_id':dataset_id,'root':workspace.relative_to(STORAGE).as_posix(),
        'production_through':outputs['produccion_real_limpio']['through']})
    return manifest
