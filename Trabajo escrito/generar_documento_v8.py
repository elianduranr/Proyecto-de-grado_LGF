"""Word de la revisión v8; no sobrescribe el texto ni el Word de la v6."""
from pathlib import Path
import json
import re
from docx import Document
from docx.shared import Cm, Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image

FOLDER=Path(__file__).resolve().parent
NAME='Documento_LaGaitana_v8_validacion_temporal_actualizada_20261028'
source=FOLDER/(NAME+'.md')
text=source.read_text(encoding='utf-8')
doc=Document();section=doc.sections[0]
section.top_margin=section.bottom_margin=section.left_margin=section.right_margin=Cm(2.54)
normal=doc.styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(12)
normal.paragraph_format.line_spacing=1.5;normal.paragraph_format.space_after=Pt(6)
normal.paragraph_format.widow_control=True
for name in ['Title','Heading 1','Heading 2','Heading 3','Caption']:
    style=doc.styles[name];style.font.name='Times New Roman';style.font.color.rgb=RGBColor(0,0,0)
    style.paragraph_format.keep_with_next=True
for name in ['Heading 1','Heading 2','Heading 3']:doc.styles[name].font.bold=True
doc.styles['Title'].font.size=Pt(18)
doc.styles['Heading 1'].font.size=Pt(14)
doc.styles['Heading 2'].font.size=Pt(12)
doc.styles['Heading 3'].font.size=Pt(12)
doc.styles['Caption'].font.size=Pt(10)
doc.styles['Caption'].paragraph_format.keep_with_next=False
footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
footer.add_run('La Gaitana · Versión 8 | ').font.size=Pt(9)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
doc.core_properties.title='Pronóstico de producción floral — revisión metodológica y conclusiones'
doc.core_properties.subject='Revisión según observaciones del profesor, 28/10/2026'
doc.core_properties.author='Elián Durán; Julián Osorio; Anderson Gonzalez'


def inline(paragraph,value):
    """Conservar énfasis sin dejar marcadores Markdown impresos."""
    for part in re.split(r'(\*\*.*?\*\*|`[^`]+`)',value):
        run=paragraph.add_run(part[2:-2] if part.startswith('**') else part.strip('`'))
        if part.startswith('**'):run.bold=True
        if '[PENDIENTE:' in part:run.italic=True


lines=text.splitlines();index=0;figures=0;tables=0
while index<len(lines):
    line=lines[index].strip()
    if not line:index+=1;continue
    if line.startswith('|'):
        rows=[]
        while index<len(lines) and lines[index].strip().startswith('|'):
            value=lines[index].strip()
            if not re.fullmatch(r'\|[\s:|\-]+\|',value):rows.append([c.strip() for c in value.strip('|').split('|')])
            index+=1
        assert rows and all(len(row)==len(rows[0]) for row in rows)
        table=doc.add_table(rows=1,cols=len(rows[0]));tables+=1;table.autofit=False
        width=section.page_width-section.left_margin-section.right_margin
        first=width*(.30 if len(rows[0])>=6 else .35)
        widths=[first]+[(width-first)/(len(rows[0])-1)]*(len(rows[0])-1)
        for column,cell_width in zip(table.columns,widths):column.width=int(cell_width)
        borders=OxmlElement('w:tblBorders')
        for edge in ['top','bottom','insideH','start','end','insideV']:
            element=OxmlElement('w:'+edge);element.set(qn('w:val'),'single' if edge in ['top','bottom','insideH'] else 'nil')
            element.set(qn('w:sz'),'4');element.set(qn('w:color'),'000000');borders.append(element)
        table._tbl.tblPr.append(borders)
        for row_index,values in enumerate(rows):
            row=table.rows[0] if row_index==0 else table.add_row()
            no_split=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(no_split)
            if row_index==0:
                repeat=OxmlElement('w:tblHeader');row._tr.get_or_add_trPr().append(repeat)
            for column_index,(cell,value) in enumerate(zip(row.cells,values)):
                cell.width=int(widths[column_index]);p=cell.paragraphs[0]
                p.paragraph_format.line_spacing=1.0;p.paragraph_format.space_after=Pt(5);p.paragraph_format.space_before=Pt(5)
                p.paragraph_format.keep_with_next=row_index==0
                inline(p,value)
                for run in p.runs:run.font.size=Pt(8.5 if len(rows[0])>=6 else 10);run.font.color.rgb=RGBColor(0,0,0)
                if row_index==0:
                    for run in p.runs:run.bold=True
                    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EEEEEE');cell._tc.get_or_add_tcPr().append(shade)
        doc.add_paragraph();continue
    figure=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line)
    if figure:
        caption,path=figure.groups();image=FOLDER/path
        if not image.exists():raise FileNotFoundError(image)
        p=doc.add_paragraph();p.paragraph_format.keep_with_next=True
        with Image.open(image) as bitmap:width_px,height_px=bitmap.size
        image_width=min(6.1,7.8*width_px/height_px)
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run().add_picture(str(image),width=Inches(image_width))
        inline(doc.add_paragraph(style='Caption'),caption);figures+=1
    elif line.startswith('# '):doc.add_heading(line[2:],level=0)
    elif re.match(r'#{2,4} ',line):
        hashes,title=line.split(' ',1);p=doc.add_heading(title,level=len(hashes)-1)
        if len(hashes)==2 and re.match(r'(?:[1-7]\.|Anexo)',title):p.paragraph_format.page_break_before=True
    else:
        p=doc.add_paragraph();inline(p,line)
    index+=1

output=FOLDER/(NAME+'.docx');doc.save(output)
check=Document(output)
assert len(check.tables)==tables
assert len(check.inline_shapes)==figures==len(re.findall(r'^!\[',text,re.M))
all_text='\n'.join([p.text for p in check.paragraphs]+[c.text for t in check.tables for r in t.rows for c in r.cells])
assert all(f'Respuesta a OE{i}' in all_text for i in range(1,5))
assert 'Respuesta al objetivo general' in all_text
assert '[PENDIENTE:' in all_text and '{{' not in all_text
report={'word':output.name,'tablas':tables,'figuras':figures,'objetivos_con_conclusion':5,
        'marcadores_pendientes':len(re.findall(r'\[PENDIENTE:',all_text)),
        'no_sobrescribe_v6':True,'maquetacion':'Times New Roman, márgenes 2,54 cm, interlineado 1,5; tablas monocromas y figuras existentes a color'}
(FOLDER/'Revision_v8/verificacion_word.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
