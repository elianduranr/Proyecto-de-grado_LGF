"""Reconsultar y versionar la ventana reciente de corte, sin escribir en WebFlor."""
import hashlib
import json
import os
from datetime import timedelta
from pathlib import Path
import pandas as pd
import pyodbc
from sqlalchemy import select
from .config import STORAGE
from .db import ActiveDataset, Audit, Dataset, Session, Upload, now

PROCEDURE='[Reporte].[InformeCorteInvVariedad]'
RETENTION_DAYS=45  # Confirmed in the procedure definition, not an inferred policy.
MAPPING={'Finca':'FINCA','Invernadero':'INVERNADERO','Fecha':'FECHA CORTE','Anio':'ANO',
         'Semana':'SEMANA','TipoCorte':'TIPO CORTE','Producto':'PRODUCTO','Grado':'GRADO',
         'Color':'COLOR','Variedad':'VARIEDAD','Tallos':'TALLOS','Lote':'LOTE',
         'EstadoInventario':'ESTADO INVENTARIO','Hora':'HORA CORTE','TipoInventario':'TIPO INVENTARIO'}


def configured():
    return all(os.getenv(name) for name in ['WEBFLOR_SERVER','WEBFLOR_DATABASE','WEBFLOR_USER','WEBFLOR_PASSWORD'])


def connect():
    if not configured():raise ValueError('La conexión de lectura a WebFlor no está configurada.')
    defaults={'WEBFLOR_DRIVER':'ODBC Driver 18 for SQL Server','WEBFLOR_TRUST_CERTIFICATE':'no'}
    names={'DRIVER':'WEBFLOR_DRIVER','SERVER':'WEBFLOR_SERVER','DATABASE':'WEBFLOR_DATABASE',
           'UID':'WEBFLOR_USER','PWD':'WEBFLOR_PASSWORD','TrustServerCertificate':'WEBFLOR_TRUST_CERTIFICATE'}
    values={key:os.getenv(variable,defaults.get(variable,'')) for key,variable in names.items()}
    conn_str=';'.join(key+'={'+value.replace('}','}}')+'}' for key,value in values.items())
    conn=pyodbc.connect(conn_str+';Encrypt=yes;ApplicationIntent=ReadOnly;',timeout=15,readonly=True)
    conn.timeout=180
    return conn


def normalized(series):
    return (series.astype('string').str.normalize('NFKD').str.replace('[\u0300-\u036f]','',regex=True)
            .str.replace(r'\s+',' ',regex=True).str.strip().str.upper()
            .replace({'':pd.NA,'NAN':pd.NA,'NONE':pd.NA,'<NA>':pd.NA}))


def validate_report(frame,start,end):
    if set(MAPPING)-set(frame):raise ValueError('El reporte de WebFlor cambió sus columnas; no se activó la descarga.')
    frame=frame.copy();frame['Fecha']=pd.to_datetime(frame.Fecha,errors='coerce').dt.normalize()
    stems=pd.to_numeric(frame.Tallos,errors='coerce')
    if frame.Fecha.isna().any() or stems.isna().any() or (stems%1!=0).any():
        raise ValueError('WebFlor devolvió fechas o cantidades no válidas; se conserva la versión anterior.')
    if any(normalized(frame[c]).isna().any() for c in ['Finca','Producto','Color','Variedad']):
        raise ValueError('WebFlor devolvió identificadores incompletos; se conserva la versión anterior.')
    if not frame.Fecha.between(pd.Timestamp(start),pd.Timestamp(end)).all():
        raise ValueError('WebFlor devolvió cortes fuera de la ventana solicitada.')
    frame['Tallos']=stems.astype('int64')
    # Preserve signed inventory adjustments, repeated legitimate cuts, and original names.
    return frame


def compare_overlap(frame,existing,raise_on_difference=True,start=None,end=None):
    source=frame.rename(columns={'Finca':'finca','Fecha':'fecha_corte','Producto':'producto',
                                'Color':'color','Variedad':'variedad','Tallos':'tallos'}).copy()
    for column in ['finca','producto','color','variedad']:source[column]=normalized(source[column])
    source.finca=source.finca.replace({'GF':'GAITANA','LA GAITANA':'GAITANA','AR':'ARABELLA'})
    start=pd.Timestamp(start) if start is not None else source.fecha_corte.min()
    end=min(pd.Timestamp(end),existing.fecha_corte.max()) if end is not None else existing.fecha_corte.max()
    keys=['finca','fecha_corte','producto','color','variedad']
    left=source.loc[source.fecha_corte.between(start,end)].groupby(keys,dropna=False).tallos.sum().rename('webflor')
    right=existing.loc[existing.fecha_corte.between(start,end)].groupby(keys,dropna=False).tallos.sum().rename('actual')
    compared=pd.concat([left,right],axis=1).fillna(0)
    compared['difference']=compared.webflor-compared.actual
    if not len(compared) and raise_on_difference:raise ValueError('No hay un período común para comprobar el empalme con WebFlor.')
    if raise_on_difference and compared.difference.ne(0).any():
        raise ValueError('Hay diferencias entre WebFlor y la producción guardada en fechas comunes. No se añadieron ni reemplazaron cortes; revise el archivo de comparación de esta descarga.')
    return compared


def window_changed(frame,existing,start,end):
    """Comparar multiconjuntos: conservar duplicados y detectar cambios de detalle."""
    columns=['finca','fecha_corte','producto','color','variedad','tallos','invernadero',
             'tipo_corte','grado','lote','estado_inventario','hora_corte','tipo_inventario','anio_fuente','semana_fuente']
    names=['finca','invernadero','fecha_corte','anio_fuente','semana_fuente','tipo_corte','producto','grado',
           'color','variedad','tallos','lote','estado_inventario','hora_corte','tipo_inventario']
    source=frame.rename(columns=dict(zip(MAPPING,names)))
    prior=existing.loc[existing.fecha_corte.between(pd.Timestamp(start),pd.Timestamp(end))].copy()
    for col in ['tipo_corte','lote','hora_corte']:
        if col+'_original' in prior:prior[col]=prior[col+'_original']
    def fingerprints(d):
        d=d.reindex(columns=columns).copy()
        for col in columns:
            if col=='fecha_corte':d[col]=pd.to_datetime(d[col]).dt.normalize().astype('string')
            elif col in ['tallos','anio_fuente','semana_fuente']:d[col]=pd.to_numeric(d[col],errors='coerce').astype('Int64').astype('string')
            elif col in ['finca','producto','color','variedad']:d[col]=normalized(d[col])
            else:d[col]=d[col].astype('string').str.strip()
        d.finca=d.finca.replace({'GF':'GAITANA','LA GAITANA':'GAITANA','AR':'ARABELLA'})
        return pd.util.hash_pandas_object(d.fillna('<NULL>'),index=False).sort_values().to_numpy()
    import numpy as np
    return not np.array_equal(fingerprints(source),fingerprints(prior))


def stage(actor,job_id,progress):
    with Session() as db:
        active=db.get(ActiveDataset,'vigente')
        if not active:raise ValueError('Primero debe terminar la carga inicial de fuentes antes de actualizar desde WebFlor.')
        dataset=db.get(Dataset,active.dataset_id)
        root=Path(dataset.root);root=root if root.is_absolute() else STORAGE/root
    path=root/'Datos_analiticos_proyecto/produccion_real_limpio.parquet'
    through=pd.Timestamp(pd.read_parquet(path,columns=['fecha_corte']).fecha_corte.max()).normalize()
    progress(2,'Reconsultando hasta ayer en WebFlor; se revisan también días ya cargados')
    with connect() as conn:
        cursor=conn.cursor();today=cursor.execute('SELECT CAST(GETDATE() AS date)').fetchval()
        start=today-timedelta(days=RETENTION_DAYS);end=today-timedelta(days=1)
        if through.date()<start-timedelta(days=1):
            raise ValueError(f'WebFlor sólo ofrece los últimos {RETENTION_DAYS} días. Cargue el histórico faltante desde {(through+pd.Timedelta(days=1)).date()} hasta {start-timedelta(days=1)} antes de actualizar por conexión.')
        cursor.execute('EXEC '+PROCEDURE+' @FechaInicial=?, @FechaFinal=?',start,end)
        while cursor.description is None:
            if not cursor.nextset():raise ValueError('El reporte WebFlor no devolvió datos.')
        columns=[column[0] for column in cursor.description];records=[]
        while batch:=cursor.fetchmany(5000):records.extend(tuple(row) for row in batch)
        frame=pd.DataFrame.from_records(records,columns=columns);conn.rollback()
    folder=STORAGE/'webflor'/job_id;folder.mkdir(parents=True,exist_ok=True)
    frame.to_parquet(folder/'reporte_original.parquet',index=False)
    frame=validate_report(frame,start,end)
    if frame.empty:raise ValueError('WebFlor devolvió una ventana vacía. No se reemplazó el histórico; revise la conexión o el reporte.')
    existing=pd.read_parquet(path,filters=[('fecha_corte','>=',pd.Timestamp(start)),('fecha_corte','<=',pd.Timestamp(end))])
    progress(4,'Auditando correcciones del período común antes de sustituir la ventana reciente')
    compared=compare_overlap(frame,existing,raise_on_difference=False,start=start,end=end)
    compared.to_parquet(folder/'comparacion_empalme.parquet')
    changed=window_changed(frame,existing,start,end)
    previous=existing.loc[existing.fecha_corte.between(pd.Timestamp(start),pd.Timestamp(end))]
    old_farms=set(normalized(previous.finca).dropna())
    new_farms=set(normalized(frame.Finca).replace({'GF':'GAITANA','LA GAITANA':'GAITANA','AR':'ARABELLA'}).dropna())
    if old_farms-new_farms:raise ValueError('El reporte no incluye todas las fincas presentes en la ventana guardada. No se sustituyeron cortes; revise el alcance del reporte.')
    new=frame.loc[frame.Fecha.gt(through)]
    report={'source':'WebFlor','procedure':PROCEDURE,'server_today':str(today),'requested_start':str(start),
            'closed_through':str(end),'previous_through':str(through.date()),'overlap_cases':len(compared),
            'overlap_different':int(compared.difference.ne(0).sum()),'new_rows':len(new),'new_stems':int(new.Tallos.sum()),
            'replacement_rows':len(frame),'previous_window_rows':len(previous),
            'replacement_stems':int(frame.Tallos.sum()),'previous_window_stems':int(previous.tallos.sum()),
            'requires_rebuild':changed,
            'received_at':now().isoformat(),'archive':folder.relative_to(STORAGE).as_posix()}
    if not changed:
        report['message']=f'Se reconsultó del {start} al {end}: sin cambios en los movimientos. Incluye ayer; no hace falta duplicar ni reprocesar cortes.'
        with Session.begin() as db:db.add(Audit(actor=actor,action='webflor_sin_cambios',object_id=job_id,details=report))
    else:
        if frame.Fecha.dt.year.nunique()!=1:
            raise ValueError('La ventana cruza años; incorporar cada año por separado antes de activar.')
        year=int(frame.Fecha.dt.year.iloc[0]);name=f'WebFlor {year} desde {start} hasta {end}.xlsx'
        if year not in range(2021,2027):raise ValueError('El formato de esta versión está validado para 2021–2026; revisar el contrato del nuevo año antes de incorporar cortes.')
        workbook=folder/name
        detail=frame[list(MAPPING)].rename(columns=MAPPING)
        detail.to_excel(workbook,sheet_name='BD',index=False)
        digest=hashlib.sha256(workbook.read_bytes()).hexdigest()
        uploads=STORAGE/'uploads';uploads.mkdir(exist_ok=True)
        import shutil
        shutil.copyfile(workbook,uploads/(digest+'.xlsx'))
        report.update(year=year,through=str(frame.Fecha.max().date()),bytes=workbook.stat().st_size,
                      replace_window={'start':str(start),'end':str(end),'received_at':report['received_at']},
                      message='Descarga validada. La nueva versión sustituirá este rango completo, incluidas sus correcciones, y conservará los cortes anteriores al rango.')
        with Session.begin() as db:
            receipt=Upload(source='produccion',filename=name,sha256=digest,mode='adicional',state='pendiente_etl',report=report)
            db.add(receipt);db.flush();report['upload_id']=receipt.id
            db.add(Audit(actor=actor,action='webflor_descargado',object_id=job_id,details=report))
    (folder/'descarga.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report
