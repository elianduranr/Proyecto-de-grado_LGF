"""Check an activated dataset and generate one real, unpublished proposal via HTTP.

Run after the API and worker have started. --wait waits for the initial ETL;
it never starts another ETL or publishes a forecast. Reports stay in storage/.
"""
import argparse
import json
import math
import time
from pathlib import Path
from urllib.request import Request, urlopen

from sqlalchemy import inspect, select, func, text
from app.config import STORAGE
from app.db import Session, engine, ActiveDataset, Dataset, Forecast, Line, SourceFile,Upload
from app.clean_tables import CLEAN_TABLES


def request(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = Request('http://127.0.0.1:8000/api' + path, data=data,
                  headers={'Content-Type': 'application/json'})
    with urlopen(req, timeout=180) as response:
        return json.load(response)


def main(dataset_id=None,wait=False):
    if dataset_id is None:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('dataset_id')
        parser.add_argument('--wait', action='store_true')
        args = parser.parse_args()
    else:args=argparse.Namespace(dataset_id=dataset_id,wait=wait)
    deadline = time.monotonic() + (3 * 3600 if args.wait else 0)
    while True:
        state = request('/data/status')
        if state['dataset_id'] == args.dataset_id and state['ready']:
            break
        job = state.get('etl_job')
        if not args.wait or time.monotonic() >= deadline or not job:
            raise RuntimeError('La ejecución esperada aún no está activa y lista; no se generó un pronóstico.')
        print('Esperando ETL:', job['message'], flush=True)
        time.sleep(30)

    with Session() as db:
        pointer = db.get(ActiveDataset, 'vigente')
        assert pointer.dataset_id == args.dataset_id
        dataset = db.get(Dataset, pointer.dataset_id)
        assert dataset.state == 'activo'
        manifest = dataset.manifest
        assert len(manifest['completed_stages']) == 11
        catalog_count = db.scalar(select(func.count()).select_from(SourceFile).where(SourceFile.active == 1))
        assert catalog_count == len(manifest['sources'])
        original_drafts = db.scalars(select(Forecast.id)).all()
        webflor_downloads=[receipt.report for upload_id in manifest.get('uploads',[]) if (receipt:=db.get(Upload,upload_id)) and receipt.report.get('source')=='WebFlor']
    inspector = inspect(engine)
    schema = 'EP' if engine.dialect.name == 'mssql' else None
    tables = inspector.get_table_names(schema=schema)
    assert all(table.name in tables for table in CLEAN_TABLES.values())
    views = inspector.get_view_names(schema=schema) if schema else []
    sql_counts={}
    if schema:
        assert all(name in views for name in ['vw_lgf_produccion_real', 'vw_lgf_clima',
                   'vw_lgf_planos_siembra', 'vw_lgf_curvas_variedad', 'vw_lgf_estimados_semanales'])
        with engine.connect() as conn:
            for view,source in [('produccion_real','produccion_real_limpio'),('clima','clima_limpio'),
                                ('planos_siembra','planos_siembra_limpio'),('curvas_variedad','curvas_variedad_limpio'),
                                ('estimados_semanales','estimados_semanales_limpio')]:
                sql_counts[source]=int(conn.scalar(text(f'SELECT COUNT_BIG(*) FROM [EP].[vw_lgf_{view}]')))
                assert sql_counts[source]==manifest['outputs'][source]['rows']
            sql_stems=int(conn.scalar(text('SELECT SUM(CAST(tallos AS bigint)) FROM [EP].[vw_lgf_produccion_real]')))
        import pyarrow.parquet as pq
        import pyarrow.compute as pc
        current_root=Path(dataset.root)
        if not current_root.is_absolute():current_root=STORAGE/current_root
        parquet_stems=int(pc.sum(pq.read_table(current_root/'Datos_analiticos_proyecto/produccion_real_limpio.parquet',columns=['tallos'])['tallos']).as_py())
        assert sql_stems==parquet_stems
    history = request('/history?horizon=1')
    assert history['test_weeks'] and history['model']['bias'] is not None and history['engineer']['bias'] is not None
    assert not state['processing_required']
    print('Datos activos:', state['origin'], 'Sin_clima; clima habilitado:', state['climate_ready'], flush=True)
    job_id = request('/forecasts', {'origin': state['origin'], 'variant': 'Sin_clima'})['job_id']
    deadline = time.monotonic() + 1800
    message = None
    while True:
        job = request('/jobs/' + job_id)
        if job['message'] != message:
            message = job['message']; print('Pronóstico:', message, flush=True)
        if job['state'] in ['completado', 'error']:
            break
        if time.monotonic() >= deadline:
            raise TimeoutError('El pronóstico sigue en curso; consultar su trabajo antes de volver a generarlo.')
        time.sleep(4)
    if job['state'] != 'completado':
        raise RuntimeError(job['message'])
    forecast_id = job['result']['forecast_id']
    run = request('/forecasts/' + forecast_id)
    assert run['state'] == 'borrador'
    assert sorted({line['horizon'] for line in run['lines']}) == [1, 2, 3, 4, 5]
    assert all(line['final'] >= 0 and math.isfinite(line['model']) for line in run['lines'])
    keys = [(line['product'], line['color'], line['variety'], line['horizon']) for line in run['lines']]
    assert len(set(keys)) == len(keys)
    with Session() as db:
        row = db.get(Forecast, forecast_id)
        assert row.metadata_json['dataset_id'] == args.dataset_id
        assert row.metadata_json['variant'] == 'Sin_clima'
        assert all(db.get(Forecast, previous) is not None for previous in original_drafts)
        assert db.scalar(select(func.count()).select_from(Line).where(Line.forecast_id == forecast_id)) == len(keys)
        metadata = row.metadata_json
    report = {'passed': True, 'dataset_id': args.dataset_id, 'origin': state['origin'],
              'sources': state['sources'], 'archived_source_files': catalog_count,
              'schema': schema, 'tables': tables, 'views': views,
              'sql_counts':sql_counts,
              'climate_ready': state['climate_ready'], 'forecast_id': forecast_id,
              'forecast_lines': len(keys), 'series': len(keys) // 5,
              'horizons': [1, 2, 3, 4, 5], 'metadata': metadata,
              'test_weeks': history['test_weeks'], 'existing_forecasts_preserved': original_drafts,
              'weekly_totals': {str(h): sum(line['final'] for line in run['lines'] if line['horizon'] == h)
                                for h in range(1, 6)}}
    path = STORAGE / 'verification_operational.json'
    if webflor_downloads:report['webflor']=webflor_downloads[-1]
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['passed', 'dataset_id', 'origin', 'forecast_id',
                     'forecast_lines', 'series', 'weekly_totals']}, ensure_ascii=False, indent=2), flush=True)
    return report


if __name__ == '__main__':
    main()
