"""Evaluaciones archivadas y seguimiento de publicaciones sin información futura."""
import pandas as pd
import json
from pathlib import Path

MODES = {
    'updated': ('Evaluación retrospectiva actualizada · cuaderno 26', 'Predicciones del 19 conservadas; producción real y estimados nominales de la última versión validada. Se recalculan los errores al cambiar las fuentes. No equivale a publicaciones anticipadas. Las semanas sin pareja nominal no se inventan.'),
    'test': ('Prueba 2026 · cuadernillo 19', 'Prueba retrospectiva conservada. No se recalcula al cargar archivos nuevos.'),
    'validation': ('Validación 2025 · selección del modelo', 'Se utilizó para comparar variantes antes de la prueba de 2026; no es una prueba independiente de la selección.'),
    'train': ('Entrenamiento · diagnóstico H1', 'Predicciones dentro de muestra del último ajuste guardado; sus fechas se muestran abajo. El modelo ya conocía esos resultados: no demuestra capacidad de anticipación. Se presenta el diagnóstico H1.'),
    'live': ('Seguimiento de nuevas semanas', 'Se actualiza con las cargas de producción real. Sólo evalúa publicaciones anteriores al inicio del origen del pronóstico, sobre semanas objetivo terminadas. Excluye borradores y simulaciones retrospectivas.'),
}


def evaluation_paths(legacy):
    from .config import STORAGE
    output=legacy/'Datos_analiticos_proyecto/validacion_temporal_20261028'
    summary=output/'resumen_ejecucion.json'
    if not summary.exists():raise FileNotFoundError('La evaluación actualizada aún no terminó. Puede consultar la prueba histórica mientras finaliza el cuaderno 26.')
    source=STORAGE/'datasets'/json.loads(summary.read_text(encoding='utf-8'))['snapshot']
    pointer=STORAGE/'metrics_source.json'
    if pointer.exists():
        info=json.loads(pointer.read_text(encoding='utf-8'))
        candidate=Path(info['root'])
        if not candidate.is_absolute():candidate=STORAGE/candidate
        if candidate.exists():source=candidate
    return output,source


def updated_frame(read,legacy,key):
    output,source=evaluation_paths(legacy)
    d=read(output/'predicciones_actualizadas.parquet')
    d=d.loc[d.modelo.eq('19_mensual_sin_clima')].copy()
    proposal=output/'pronostico_mas_reciente.parquet'
    if proposal.exists():d=pd.concat([d,read(proposal).rename(columns={'fecha_calculo':'calculated_at'})],ignore_index=True)
    cols=key+['origen','semana_objetivo','horizonte','prediccion']
    d=d[cols].drop_duplicates(key+['origen','semana_objetivo','horizonte'],keep='first')
    actual=read(source/'Datos_analiticos_proyecto/modelo_con_proyecciones_teoricas/produccion_clima_semanal.parquet')
    actual=actual.rename(columns={'semana_inicio':'semana_objetivo','tallos_reales':'y'})
    manifest=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    through=pd.Timestamp(manifest['outputs']['produccion_real_limpio']['through'])
    now=pd.Timestamp.now(tz='America/Bogota').tz_localize(None).normalize()
    d=d.loc[(d.semana_objetivo+pd.Timedelta(days=7)).le(now)&(d.semana_objetivo+pd.Timedelta(days=6)).le(through)]
    d=d.merge(actual[key+['semana_objetivo','y']],on=key+['semana_objetivo'],how='inner',validate='many_to_one')
    d=d.rename(columns={'prediccion':'Seleccion_pre2026'})
    result=d.merge(engineer_archive(source,read,key),on=key+['origen','semana_objetivo','horizonte'],how='left',validate='one_to_one')
    result.attrs.update(source_version=manifest['id'],source_through=str(through.date()))
    return result


def eligible_publications(frame, today):
    """Una publicación posterior al origen no es una predicción anticipada."""
    origin_utc = pd.to_datetime(frame.origen).dt.tz_localize('America/Bogota').dt.tz_convert('UTC')
    return frame.loc[(pd.to_datetime(frame.published_at, utc=True) < origin_utc) &
                     (pd.to_datetime(frame.semana_objetivo) + pd.Timedelta(days=7) <= pd.Timestamp(today).normalize())]


def engineer_archive(root, read, key):
    e = read(root/'Datos_analiticos_proyecto/estimados_semanales_limpio.parquet')
    e = e.loc[e.en_h1_h5 & ~e.es_ajustado & ~e.archivo_es_posterior &
              e.origen_solicitado.eq(e.origen_nominal) & e.horizonte_nominal.between(1, 5)].copy()
    # Conserva H1 nominal del archivo; nunca convierte la semana en curso en H1.
    e = e.rename(columns={'origen_nominal':'origen', 'semana_inicio':'semana_objetivo', 'horizonte_nominal':'horizonte'})
    # La fuente también contiene un horizonte de respaldo: no usarlo aquí.
    e = e.loc[:, ~e.columns.duplicated(keep='first')]
    cols = key + ['origen', 'semana_objetivo', 'horizonte']
    if not e.groupby(cols).archivo_origen.nunique().le(1).all():
        raise ValueError('Más de un archivo nominal para el mismo caso: revisar el ETL de estimados.')
    g=e.groupby(cols).estimado
    result=g.sum(min_count=1).where(g.count().eq(g.size()))
    return result.rename('ingeniero').reset_index()


def frame(mode, read, review, legacy, runtime_root, weekly, key):
    if mode=='updated':return updated_frame(read,legacy,key)
    if mode == 'test':
        d = read(review/'comparacion_clima_curvas_2026.parquet')
        return d.loc[d.grupo_comparacion.eq('principal_estricta_nominal')].copy()
    if mode in ('train', 'validation'):
        if mode == 'train':
            new=legacy/'Datos_analiticos_proyecto/validacion_temporal_20261028/predicciones_train_ultimo_ajuste.parquet'
            if new.exists():
                d=read(new).rename(columns={'prediccion':'Seleccion_pre2026'})
                d=d.loc[d.horizonte.eq(1)].copy()
                _,source=evaluation_paths(legacy)
                return d.merge(engineer_archive(source,read,key),on=key+['origen','semana_objetivo','horizonte'],how='left',validate='one_to_one')
            d = read(review/'predicciones_train_h1_ultimo_ajuste.parquet')
            d = d.loc[d.modelo.eq('Sin_clima')].rename(columns={'prediccion_train':'Seleccion_pre2026'})
        else:
            d = read(review/'validacion_clima_pre2026.parquet').rename(columns={'Sin_clima':'Seleccion_pre2026'})
        return d.merge(engineer_archive(legacy, read, key), on=key+['origen','semana_objetivo','horizonte'], how='left', validate='one_to_one')
    from .db import Session, Publication, Forecast, Line
    from sqlalchemy import select
    columns = key+['origen','semana_objetivo','horizonte','y','Seleccion_pre2026','ingeniero']
    with Session() as db:
        rows = db.execute(select(Forecast.farm, Line.product, Line.color, Line.variety,
            Forecast.origin, Line.target, Line.horizon, Line.model_value, Publication.published_at)
            .join(Publication, Publication.forecast_id==Forecast.id)
            .join(Line, Line.forecast_id==Forecast.id)).all()
    if not rows:
        return pd.DataFrame(columns=columns)
    d = pd.DataFrame(rows, columns=key+['origen','semana_objetivo','horizonte','Seleccion_pre2026','published_at'])
    d = eligible_publications(d, pd.Timestamp.now(tz='America/Bogota').date())
    for col in ['origen', 'semana_objetivo']: d[col] = pd.to_datetime(d[col])
    actual = weekly().rename(columns={'semana_inicio':'semana_objetivo','tallos_reales':'y'})
    d = d.merge(actual[key+['semana_objetivo','y']], on=key+['semana_objetivo'], validate='many_to_one')
    return d.merge(engineer_archive(runtime_root(), read, key), on=key+['origen','semana_objetivo','horizonte'], how='left', validate='one_to_one')
