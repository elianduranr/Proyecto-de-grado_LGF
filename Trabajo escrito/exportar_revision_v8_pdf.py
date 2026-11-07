"""Verificación de paginado en una instancia oculta e independiente de Word."""
from pathlib import Path
import json
import pythoncom
import win32com.client

folder=Path(__file__).resolve().parent
name='Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028'
pythoncom.CoInitialize();word=None;document=None
try:
    word=win32com.client.DispatchEx('Word.Application')
    word.Visible=False;word.DisplayAlerts=0
    document=word.Documents.Open(str(folder/(name+'.docx')),ReadOnly=True,AddToRecentFiles=False)
    document.Repaginate()
    pages=document.ComputeStatistics(2)
    document.ExportAsFixedFormat(str(folder/(name+'.pdf')),17,OpenAfterExport=False)
    heading_pages={}
    for title in ['1. Introducción','4.3.1. Límite','5.1. Referencia','5.1.2. Qué cambió','5.3.1. Resultado','7. Conclusiones','Anexo C. Pendientes']:
        area=document.Content.Duplicate
        if area.Find.Execute(FindText=title,MatchCase=True):heading_pages[title]=area.Information(3)
    report={'paginas_word':pages,'tablas':document.Tables.Count,'figuras':document.InlineShapes.Count,
            'pdf':name+'.pdf','word_original_no_modificado':True,'instancia_oculta_independiente':True,'paginas_secciones':heading_pages}
    (folder/'Revision_v8/verificacion_paginado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
finally:
    if document is not None:document.Close(False)
    if word is not None:word.Quit(False)
    pythoncom.CoUninitialize()
