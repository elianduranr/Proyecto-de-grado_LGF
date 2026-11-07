"""Verifica la ventana real por lectura; no activa fuentes ni crea trabajos."""
import json
from datetime import timedelta
from pathlib import Path
import pandas as pd
from app.webflor import connect,validate_report,PROCEDURE,RETENTION_DAYS,compare_overlap,window_changed
from app.data import runtime_paths
from app.config import STORAGE

with connect() as conn:
    cursor=conn.cursor();today=cursor.execute('SELECT CAST(GETDATE() AS date)').fetchval()
    start=today-timedelta(days=RETENTION_DAYS);end=today-timedelta(days=1)
    cursor.execute('EXEC '+PROCEDURE+' @FechaInicial=?, @FechaFinal=?',start,end)
    while cursor.description is None:
        if not cursor.nextset():raise ValueError('WebFlor no devolvió datos.')
    columns=[col[0] for col in cursor.description];rows=[]
    while batch:=cursor.fetchmany(5000):rows.extend(tuple(row) for row in batch)
    report=pd.DataFrame.from_records(rows,columns=columns);conn.rollback()
archive=STORAGE/'webflor_checks'/str(today);archive.mkdir(parents=True,exist_ok=True)
report.to_parquet(archive/'reporte_original.parquet',index=False)
report=validate_report(report,start,end)
if report.empty:raise ValueError('Ventana vacía; no se validó un reemplazo.')
path=runtime_paths()[1]/'produccion_real_limpio.parquet'
old=pd.read_parquet(path,filters=[('fecha_corte','>=',pd.Timestamp(start)),('fecha_corte','<=',pd.Timestamp(end))])
comparison=compare_overlap(report,old,False,start,end)
comparison.to_parquet(archive/'comparacion.parquet')
result={'passed':True,'read_only':True,'server_today':str(today),'requested_start':str(start),'closed_through':str(end),
        'report_rows':len(report),'latest_report_cut':str(report.Fecha.max().date()),
        'farms':sorted(report.Finca.dropna().astype(str).unique().tolist()),
        'previous_window_rows':len(old),'changed_overlap_groups':int(comparison.difference.ne(0).sum()),
        'requires_rebuild':window_changed(report,old,start,end),
        'tail_days':{str(dt.date()):int(n) for dt,n in report.groupby('Fecha').size().tail(5).items()}}
(STORAGE/'verification_webflor_refresh_source.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
