"""Actualiza campos de Word, exporta PDF y comprueba el límite real de 50 páginas."""
from pathlib import Path
import sys,json,hashlib
import pythoncom,win32com.client
sys.stdout.reconfigure(encoding='utf8')
from revision_v9_config import NAME
F=Path(__file__).resolve().parent;O=F/'Revision_v9'
pythoncom.CoInitialize();app=None;doc=None
try:
    app=win32com.client.DispatchEx('Word.Application');app.Visible=False;app.DisplayAlerts=0
    doc=app.Documents.Open(str(F/(NAME+'.docx')),ReadOnly=False,AddToRecentFiles=False)
    doc.Fields.Update()
    for toc in doc.TablesOfContents:
        toc.Update()
        # El Word local puede importar su estilo de índice: fijar aquí el formato real del campo.
        toc.Range.Font.Name='Times New Roman';toc.Range.Font.Size=11
        pf=toc.Range.ParagraphFormat;pf.SpaceBefore=0;pf.SpaceAfter=2;pf.LineSpacingRule=0
        pf.KeepWithNext=False;pf.KeepTogether=False;pf.PageBreakBefore=False
    doc.Repaginate()
    for toc in doc.TablesOfContents:toc.UpdatePageNumbers()
    doc.Save()
    doc.ExportAsFixedFormat(str(F/(NAME+'.pdf')),17,OpenAfterExport=False)
    pages=int(doc.ComputeStatistics(2));locations={}
    titles=['Resumen','1. Introducción','2. Radiografía','3. Metodología','4. Resultados y discusión','5. Conclusiones','Referencias','Anexo A.','Anexo B.','Anexo C.']
    for paragraph in doc.Paragraphs:
        value=paragraph.Range.Text.strip()
        matches=[title for title in titles if value.startswith(title)]
        if matches and int(paragraph.OutlineLevel)<=3:
            for title in matches:locations.setdefault(title,int(paragraph.Range.Information(3)))
    report={'paginas_word':pages,'maximo':50,'cumple_limite':pages<=50,'tablas':int(doc.Tables.Count),'figuras':int(doc.InlineShapes.Count),'indice_actualizado':True,'paginas_secciones':locations}
    (O/'verificacion_paginado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    assert pages<=50,f'La edición ocupa {pages} páginas; requiere síntesis editorial.'
finally:
    if doc is not None:doc.Close(False)
    if app is not None:app.Quit(False)
    pythoncom.CoUninitialize()
