"""El reemplazo de días debe atravesar la limpieza 05 real, no sólo un helper."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
import pandas as pd
from app.config import LEGACY
from app.webflor import MAPPING


def test_real_production_notebook_replaces_window_before_aggregation(tmp_path):
    source=LEGACY/'Notebooks/Limpieza data, Notebooks y Scripts/05_limpieza_produccion_real.ipynb'
    notebook=tmp_path/'Notebooks/05_limpieza_produccion_real.ipynb'
    notebook.parent.mkdir();shutil.copyfile(source,notebook)
    data=tmp_path/'Datos/Producción real';data.mkdir(parents=True)
    sheets={2021:['Sheet1'],2022:['Sheet1'],2023:['Sheet1','Hoja1'],
            2024:['Sheet1','sem 45 en adelante'],2025:['01-44','45-52'],2026:['BD']}
    def frame(dates,stems):
        rows=[]
        for dt,n in zip(dates,stems):
            row={col:None for col in MAPPING.values()}
            row.update({'FINCA':'GAITANA','FECHA CORTE':pd.Timestamp(dt),'TALLOS':n,
                'PRODUCTO':'Minicarnation','COLOR':'White','VARIEDAD':'Test','TIPO CORTE':'CORTE','LOTE':1,'HORA CORTE':'12:00:00'})
            rows.append(row)
        return pd.DataFrame(rows)
    for year,names in sheets.items():
        with pd.ExcelWriter(data/f'Produccion {year}.xlsx') as book:
            for name in names:
                rows=frame(['2026-10-09','2026-10-10','2026-10-11','2026-10-13'],[5,10,20,30]) if year==2026 else frame([f'{year}-01-11'],[1])
                rows.to_excel(book,sheet_name=name,index=False)
    replacement=data/'2026_webflor.xlsx'
    frame(['2026-10-10','2026-10-10'],[7,7]).to_excel(replacement,sheet_name='BD',index=False)
    (tmp_path/'manifest.json').write_text(json.dumps({'sources':[{
        'source':'produccion','path':replacement.relative_to(tmp_path).as_posix(),'sha256':'b',
        'replace_window':{'start':'2026-10-10','end':'2026-10-12','received_at':'2026-10-13'}}]}),encoding='utf-8')
    env={**os.environ,'PYTHONPATH':str(Path(__file__).resolve().parents[1]),'PYTHONIOENCODING':'utf-8','MPLBACKEND':'Agg'}
    run=subprocess.run([sys.executable,'-m','app.etl_notebook',str(notebook),str(tmp_path),'-'],
                       env=env,capture_output=True,text=True,encoding='utf-8',timeout=60)
    assert run.returncode==0,run.stdout+'\n'+run.stderr
    result=pd.read_parquet(tmp_path/'Datos_analiticos_proyecto/produccion_real_limpio.parquet')
    result=result.loc[result.fecha_corte.dt.year.eq(2026)]
    assert sorted(result.tallos.tolist())==[5,7,7,30]
    assert result.fecha_corte.max()==pd.Timestamp('2026-10-13')
    assert result.loc[result.fecha_corte.eq('2026-10-13'),'fila_excel'].tolist()==[5]
