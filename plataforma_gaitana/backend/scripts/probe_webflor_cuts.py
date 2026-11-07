"""Archive the report's currently available closed days and compare the overlap."""
import json
from datetime import timedelta
import pandas as pd
from .inspect_webflor import connection
from app.config import STORAGE


def main():
    with connection() as conn:
        cursor=conn.cursor()
        today=cursor.execute('SELECT CAST(GETDATE() AS date)').fetchval()
        start=today-timedelta(days=45);end=today-timedelta(days=1)
        conn.timeout=180
        cursor.execute('EXEC [Reporte].[InformeCorteInvVariedad] @FechaInicial=?, @FechaFinal=?',start,end)
        while cursor.description is None:
            if not cursor.nextset():raise RuntimeError('El reporte no devolvió un conjunto de datos.')
        columns=[column[0] for column in cursor.description]
        data=[]
        while batch:=cursor.fetchmany(5000):data.extend(tuple(row) for row in batch)
        frame=pd.DataFrame.from_records(data,columns=columns)
        conn.rollback()
    out=STORAGE/'webflor';out.mkdir(exist_ok=True)
    frame.to_parquet(out/'probe_closed_days.parquet',index=False)
    info={'server_today':str(today),'requested_start':str(start),'requested_end':str(end),
          'rows':len(frame),'columns':columns}
    if len(frame):
        info['dates']={name:{'min':str(frame[name].min()),'max':str(frame[name].max())}
                       for name in ['Fecha','FechaDescarga'] if name in frame}
        info['farms']=frame.groupby('Finca',dropna=False).agg(rows=('Tallos','size'),stems=('Tallos','sum')).reset_index().to_dict('records')
    (out/'probe_closed_days.json').write_text(json.dumps(info,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    print(json.dumps(info,ensure_ascii=False,indent=2,default=str),flush=True)


if __name__=='__main__':main()
