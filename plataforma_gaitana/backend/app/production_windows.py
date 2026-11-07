"""Precedencia de ventanas WebFlor antes de la limpieza canónica 05.

Se conserva el archivo original. Sólo se filtran las filas que serán sustituidas
en la copia aislada de una nueva ejecución; nunca se edita una versión activa.
"""
import json
from pathlib import Path
import pandas as pd


def filter_replaced_rows(frame, source, windows):
    column=next((c for c in frame if str(c).strip().upper()=='FECHA CORTE'),None)
    if column is None or frame.empty:
        return frame
    dates=pd.to_datetime(frame[column],format='mixed',errors='coerce')
    numbers=pd.to_numeric(frame[column].astype('string'),errors='coerce')
    serial=numbers.between(20000,80000)
    dates.loc[serial]=pd.to_datetime(numbers.loc[serial],unit='D',origin='1899-12-30')
    dates=dates.dt.normalize()
    own=next((w for w in windows if w['path']==source),None)
    priority=lambda w:(w['replace_window']['received_at'],w['sha256'])
    keep=pd.Series(True,index=frame.index)
    if own:
        scope=own['replace_window']
        if dates.isna().any() or not dates.between(scope['start'],scope['end']).all():
            raise ValueError('La descarga WebFlor contiene filas fuera de su ventana validada.')
    for window in windows:
        if own and priority(window)<=priority(own):continue
        scope=window['replace_window']
        keep &= ~dates.between(scope['start'],scope['end'])
    return frame.loc[keep].copy()


def reader(workspace):
    root=Path(workspace)
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    windows=[r for r in manifest['sources'] if r['source']=='produccion' and r.get('replace_window')]
    def read_excel(io,*args,**kwargs):
        result=pd.read_excel(io,*args,**kwargs)
        if not windows or not isinstance(result,pd.DataFrame) or kwargs.get('nrows') is not None:
            return result
        filename=Path(io._io if isinstance(io,pd.ExcelFile) else io)
        relative=filename.relative_to(root).as_posix()
        return filter_replaced_rows(result,relative,windows)
    return read_excel
