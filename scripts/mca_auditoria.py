"""Imputación retrospectiva con referencias estables y auditoría del pico de 2021."""
import numpy as np
import pandas as pd
from pathlib import Path
import hashlib

LLAVES = ['producto', 'color', 'variedad']


def muestras_fuente(bloques, carpeta, cache):
    """Primeras dos filas de cada bloque, incluyendo columnas descartadas del análisis."""
    from python_calamine import CalamineWorkbook
    parts = []
    for (file, sheet), rows in bloques.groupby(['archivo_origen', 'hoja_origen']):
        path = Path(carpeta)/file
        wanted = sorted({int(n)+offset for n in rows.fila_inicial for offset in [0,1]})
        key = hashlib.sha256(f'{path}|{path.stat().st_mtime_ns}|{path.stat().st_size}|{sheet}|{wanted}'.encode()).hexdigest()[:20]
        target = Path(cache)/('muestra_pico_'+key+'.parquet')
        if target.exists():
            parts.append(pd.read_parquet(target)); continue
        records = []
        with CalamineWorkbook.from_path(str(path)) as book:
            for i, row in enumerate(book.get_sheet_by_name(sheet).iter_rows(), 1):
                if i == 1:
                    header = [str(v).strip() or f'columna_sin_encabezado_{j+1}' for j,v in enumerate(row)]
                if i in wanted:
                    # Solo trazabilidad: no reintroducir el supervisor en el estudio.
                    record = {k:str(v) for k,v in zip(header,row) if k.lower() != 'sector'}
                    record.update(archivo_origen=file, hoja_origen=sheet, fila_origen=i)
                    records.append(record)
                if i >= max(wanted): break
        sample = pd.DataFrame(records)
        sample.to_parquet(target, index=False)
        parts.append(sample)
    return pd.concat(parts, ignore_index=True)


def referencias_estables(conteos, minimo=30, dominancia=.95, min_anios=2):
    """Solo categorías dominantes coincidentes en TODOS los años disponibles del grupo."""
    keys = LLAVES + ['anio']
    annual = conteos.groupby(keys + ['categoria'], observed=True, as_index=False).n.sum()
    annual['total'] = annual.groupby(keys, observed=True).n.transform('sum')
    annual['fraccion'] = annual.n / annual.total
    best = annual.sort_values(['n', 'categoria'], ascending=[False, True]).drop_duplicates(keys)
    summary = best.groupby(LLAVES, observed=True).agg(
        categoria=('categoria', 'first'), categorias=('categoria', 'nunique'),
        anios_donantes=('anio', 'size'), minimo_registros_anio=('total', 'min'),
        acuerdo_minimo=('fraccion', 'min'), registros_donantes=('total', 'sum'))
    return summary.loc[(summary.categorias == 1) & (summary.anios_donantes >= min_anios)
                       & (summary.minimo_registros_anio >= minimo)
                       & (summary.acuerdo_minimo >= dominancia)]


def imputar_sin_perder(df, minimo=30, dominancia=.95):
    """Añade columnas; nunca reemplaza observados ni tallos. No usa imputados como donantes.

    Valida dejando fuera un año completo. El acuerdo de donantes NO es una probabilidad
    calibrada. Los faltantes sin referencia pasan a una etiqueta, no a una categoría inventada.
    """
    assert df.finca.eq('GAITANA').all()
    validacion, resumen, referencias = [], [], []
    for col in ['grado', 'tipo_corte']:
        observed = df[col].notna()
        if col == 'tipo_corte':
            observed &= ~df.corte_imputado  # Excluir la imputación local del notebook 03.
        counts = (df.loc[observed].groupby(LLAVES + ['anio', col], observed=True)
                  .agg(n=('tallos', 'size'), tallos=('tallos', 'sum'))
                  .reset_index().rename(columns={col: 'categoria'}))
        # Validación por años: nunca se entrena con datos del año evaluado.
        for year in sorted(counts.anio.unique()):
            ref = referencias_estables(counts.loc[counts.anio.ne(year)], minimo, dominancia)
            test = counts.loc[counts.anio.eq(year)].merge(
                ref[['categoria']].rename(columns={'categoria': 'prediccion'}),
                on=LLAVES, how='left', validate='many_to_one')
            covered = test.prediccion.notna()
            correct = covered & test.categoria.eq(test.prediccion)
            n, t = test.loc[covered, 'n'].sum(), test.loc[covered, 'tallos'].sum()
            validacion.append(dict(variable=col, anio_evaluado=year,
                conocidos=int(test.n.sum()), evaluables=int(n),
                cobertura_pct=100*n/test.n.sum(),
                acierto_pct=100*test.loc[correct, 'n'].sum()/n if n else np.nan,
                acierto_tallos_pct=100*test.loc[correct, 'tallos'].sum()/t if t else np.nan))
        ref = referencias_estables(counts, minimo, dominancia)
        # No trasladar una regla histórica que falla al ocultar años conocidos.
        folds = [r for r in validacion if r['variable'] == col and r['evaluables'] >= 1000]
        enabled = bool(folds) and all(min(r['acierto_pct'], r['acierto_tallos_pct']) >= 90 for r in folds)
        for r in validacion:
            if r['variable'] == col:
                r['regla_habilitada'] = enabled
        referencias.append(ref.reset_index().assign(variable=col, regla_habilitada=enabled))
        if not enabled:
            ref = ref.iloc[:0]
        analysis, method = col+'_analisis', col+'_metodo'
        df[analysis] = df[col].astype('string').copy()
        df[method] = pd.Series('observado', index=df.index, dtype='string')
        if col == 'tipo_corte':
            df.loc[df.corte_imputado, method] = 'moda_local_notebook03'
        missing = df[col].isna()
        ix = pd.MultiIndex.from_frame(df.loc[missing, LLAVES])
        predicted = ref.reindex(ix)
        df.loc[missing, analysis] = predicted.categoria.to_numpy()
        df.loc[missing, method] = np.where(predicted.categoria.notna(),
                                          'referencia_estable_entre_anios', 'sin_referencia')
        df[analysis] = df[analysis].fillna('SIN_REFERENCIA')
        for measure in ['acuerdo_minimo', 'anios_donantes', 'registros_donantes']:
            name = col+'_'+measure
            df[name] = np.nan
            df.loc[missing, name] = predicted[measure].to_numpy(dtype=float, na_value=np.nan)
        df[col+'_imputado'] = df[method].isin(['moda_local_notebook03', 'referencia_estable_entre_anios'])
        yearly = df.groupby(['anio', method], dropna=False, observed=True).agg(
            registros=('tallos', 'size'), tallos=('tallos', 'sum')).reset_index()
        resumen.append(yearly.rename(columns={method: 'metodo'}).assign(variable=col))
        # Categorías reales preservadas exactamente; solo se añaden columnas analíticas.
        pd.testing.assert_series_equal(df.loc[df[col].notna(), analysis],
                                       df.loc[df[col].notna(), col].astype('string'), check_names=False)
    return pd.concat(resumen, ignore_index=True), pd.DataFrame(validacion), pd.concat(referencias, ignore_index=True)


def auditar_pico_2021(df):
    """Señala el máximo semanal y bloques contiguos del Excel; no elimina filas."""
    weekly = df.loc[df.anio.eq(2021)].groupby('semana').agg(
        tallos=('tallos', 'sum'), registros=('tallos', 'size')).reset_index()
    if weekly.empty:
        return {'semanas': weekly}
    q1, q3 = weekly.tallos.quantile([.25, .75])
    weekly['umbral_IQR'] = q3 + 1.5*(q3-q1)
    weekly['alerta_IQR'] = weekly.tallos.gt(weekly.umbral_IQR)
    week = int(weekly.loc[weekly.tallos.idxmax(), 'semana'])
    selected = df.anio.eq(2021) & df.semana.eq(week)
    detail = df.loc[selected].sort_values(['archivo_origen', 'hoja_origen', 'fila_origen']).copy()
    origins = detail.archivo_origen + '|' + detail.hoja_origen
    starts = origins.ne(origins.shift()) | detail.fila_origen.diff().ne(1)
    detail['bloque_fuente'] = starts.cumsum().astype(int)
    blocks = detail.groupby(['archivo_origen', 'hoja_origen', 'bloque_fuente']).agg(
        fila_inicial=('fila_origen', 'min'), fila_final=('fila_origen', 'max'),
        registros=('tallos', 'size'), tallos=('tallos', 'sum')).reset_index()
    df['alerta_pico_2021'] = selected
    df['bloque_pico_2021'] = pd.Series(pd.NA, index=df.index, dtype='Int64')
    df.loc[detail.index, 'bloque_pico_2021'] = detail.bloque_fuente
    keys = ['fecha_corte', 'producto', 'color', 'variedad', 'invernadero', 'tallos']
    similarities = []
    ids = blocks.bloque_fuente.tolist()
    for i, a in enumerate(ids):
        for b in ids[i+1:]:
            pair = detail.loc[detail.bloque_fuente.isin([a,b])]
            counts = pair.groupby(keys+['bloque_fuente'], dropna=False).size().unstack(fill_value=0)
            overlap = counts[[a,b]].min(axis=1)
            n = int(overlap.sum())
            similarities.append(dict(bloque_a=a, bloque_b=b, registros_coincidentes=n,
                porcentaje_bloque_menor=100*n/min((pair.bloque_fuente==a).sum(), (pair.bloque_fuente==b).sum()),
                tallos_coincidentes=float(np.sum(overlap.to_numpy()*counts.index.get_level_values('tallos').to_numpy()))))
    scenarios = [dict(escenario='Observado: conservar todos', tallos=float(detail.tallos.sum()))]
    for row in blocks.itertuples():
        scenarios.append(dict(escenario=f'Hipótesis: bloque {row.bloque_fuente} es copia',
                              tallos=float(detail.tallos.sum()-row.tallos)))
    return dict(semana=week, semanas=weekly, detalle=detail, bloques=blocks,
                coincidencias=pd.DataFrame(similarities), escenarios=pd.DataFrame(scenarios),
                productos=detail.groupby(['bloque_fuente','producto']).tallos.sum().reset_index(),
                dias=detail.groupby(['bloque_fuente','fecha_corte']).tallos.sum().reset_index())
