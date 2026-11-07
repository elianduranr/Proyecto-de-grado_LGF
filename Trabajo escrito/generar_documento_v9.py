"""Renderiza Word con referencias cruzadas reales desde la fuente reproducible v9."""
from pathlib import Path
import sys,json,re
from docx import Document
from docx.shared import Cm,Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image
sys.stdout.reconfigure(encoding='utf8')
from revision_v9_config import NAME
F=Path(__file__).resolve().parent;O=F/'Revision_v9'
text=(F/(NAME+'.md')).read_text(encoding='utf8');refs=json.loads((O/'objetos_y_referencias.json').read_text(encoding='utf8'))
doc=Document();sec=doc.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Cm(2.54)
sec.different_first_page_header_footer=True
style=doc.styles['Normal'];style.font.name='Times New Roman';style.font.size=Pt(12)
style.paragraph_format.line_spacing=1.5;style.paragraph_format.space_after=Pt(6);style.paragraph_format.widow_control=True
style.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
for name in ['Title','Heading 1','Heading 2','Heading 3','Caption']:
    ss=doc.styles[name];ss.font.name='Times New Roman';ss.font.color.rgb=RGBColor(0,0,0)
    ss.paragraph_format.keep_with_next=True;ss.paragraph_format.page_break_before=False
    ss.paragraph_format.space_before=Pt(10);ss.paragraph_format.space_after=Pt(5)
    ss.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
for name,size in [('Title',18),('Heading 1',14),('Heading 2',12),('Heading 3',12),('Caption',10.5)]:doc.styles[name].font.size=Pt(size)
for name in ['TOC 1','TOC 2']:
    ss=doc.styles[name] if name in doc.styles else doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
    ss.font.name='Times New Roman';ss.font.size=Pt(11);ss.font.color.rgb=RGBColor(0,0,0)
    ss.paragraph_format.line_spacing=1;ss.paragraph_format.space_before=Pt(0);ss.paragraph_format.space_after=Pt(3)
    ss.paragraph_format.keep_with_next=False
    ss.paragraph_format.left_indent=Cm(.45 if name=='TOC 2' else 0)
doc.styles['Caption'].font.italic=False;doc.styles['Caption'].paragraph_format.line_spacing=1
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
page=OxmlElement('w:fldSimple');page.set(qn('w:instr'),'PAGE');footer._p.append(page)
settings=doc.settings.element;update=OxmlElement('w:updateFields');update.set(qn('w:val'),'true');settings.append(update)
doc.core_properties.title='Análisis de pronósticos semanales y diarios de corte de productos en La Gaitana Farms'
doc.core_properties.author='Elián Durán; Julián Osorio; Anderson Gonzalez'
doc.core_properties.subject='Revisión académica según indicaciones consolidadas del asesor Rafael Amaya Gomez'
bookmark_id=0;cross_fields=0
def ref_field(p,key):
    global cross_fields
    spec=refs[key];field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),f' REF {key} \\h ')
    r=OxmlElement('w:r');t=OxmlElement('w:t');t.text=f"{spec['kind']} {spec['number']}";r.append(t);field.append(r);p._p.append(field);cross_fields+=1
def inline(p,value):
    for part in re.split(r'(@(?:tab|fig)_[a-z_]+|\*\*.*?\*\*|\*[^*]+\*|`[^`]+`)',value):
        if re.fullmatch(r'@(?:tab|fig)_[a-z_]+',part):ref_field(p,part[1:]);continue
        bold=part.startswith('**');italic=not bold and part.startswith('*');code=part.startswith('`')
        s=part[2:-2] if bold else part[1:-1] if italic or code else part
        run=p.add_run(s);run.bold=bold;run.italic=italic
def caption(label,key):
    global bookmark_id
    p=doc.add_paragraph(style='Caption');bookmark_id+=1
    a=OxmlElement('w:bookmarkStart');a.set(qn('w:id'),str(bookmark_id));a.set(qn('w:name'),key);p._p.append(a)
    spec=refs[key];p.add_run(f"{spec['kind']} {spec['number']}")
    z=OxmlElement('w:bookmarkEnd');z.set(qn('w:id'),str(bookmark_id));p._p.append(z)
    p.add_run('. '+spec['caption']);return p
def add_table(rows):
    n=len(rows[0]);t=doc.add_table(rows=1,cols=n);t.autofit=False
    if n==8:widths=[1.7,.50,.68,.68,.68,.68,.68,.66]
    elif n==4:widths=[1.45,1,1.5,2.05]
    elif n==3:widths=[1.45,2.65,1.9]
    else:widths=[2,4]
    for col,width in zip(t.columns,widths):col.width=Inches(width)
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','bottom','insideH','start','end','insideV']:
        el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single' if edge in ['top','bottom','insideH'] else 'nil');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'000000');borders.append(el)
    t._tbl.tblPr.append(borders)
    for ri,values in enumerate(rows):
        row=t.rows[0] if ri==0 else t.add_row();trpr=row._tr.get_or_add_trPr();ns=OxmlElement('w:cantSplit');trpr.append(ns)
        if ri==0:repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
        for ci,(cell,value) in enumerate(zip(row.cells,values)):
            cell.width=Inches(widths[ci]);p=cell.paragraphs[0]
            p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.line_spacing=1
            p.paragraph_format.space_before=Pt(3);p.paragraph_format.space_after=Pt(3)
            p.paragraph_format.keep_with_next=(ri<len(rows)-1) if len(rows)<=10 else ri==0
            inline(p,value)
            for run in p.runs:run.font.size=Pt(9 if n==8 else 10);run.bold=ri==0 or run.bold
            if ri==0:sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EEEEEE');cell._tc.get_or_add_tcPr().append(sh)
    return t
lines=text.splitlines();i=0;cover=True;nf=nt=0
while i<len(lines):
    line=lines[i].strip()
    if not line:i+=1;continue
    if line=='<!-- PORTADA_FIN -->':cover=False;doc.add_page_break();i+=1;continue
    if line=='<!-- CONTENIDO -->':
        doc.add_page_break()
        p=doc.add_paragraph();p.add_run('Contenido').bold=True;p.paragraph_format.keep_with_next=True
        p=doc.add_paragraph();field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'TOC \\o "1-2" \\h \\z \\u');p._p.append(field)
        doc.add_page_break();i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            row=lines[i].strip()
            if not re.fullmatch(r'\|[\s:|\-]+\|',row):rows.append([c.strip() for c in row.strip('|').split('|')])
            i+=1
        assert all(len(x)==len(rows[0]) for x in rows);add_table(rows);nt+=1;continue
    match=re.fullmatch(r'!\[(.*?)\]\((.*?)\) \{#([^}]+)\}',line)
    if match:
        title,path,key=match.groups();img=F/path
        with Image.open(img) as im:ww,hh=im.size
        width=min(6.3,(7.05 if key=='fig_clima' else 4.05)*ww/hh);p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(2);p.paragraph_format.keep_with_next=True
        p.add_run().add_picture(str(img),width=Inches(width));cp=caption(title,key);cp.paragraph_format.keep_with_next=False;nf+=1
    elif re.fullmatch(r'Tabla \d+\. .*? \{#([^}]+)\}',line):
        key=re.search(r'\{#([^}]+)\}',line).group(1);caption(line,key)
    elif line.startswith('# '):
        p=doc.add_heading(line[2:],level=0);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(65);p.paragraph_format.space_after=Pt(45)
        border=OxmlElement('w:pBdr');bottom=OxmlElement('w:bottom');bottom.set(qn('w:val'),'nil');border.append(bottom);p._p.get_or_add_pPr().append(border)
        for run in p.runs:run.font.name='Times New Roman';run.font.size=Pt(18);run.font.color.rgb=RGBColor(0,0,0)
    elif re.match(r'#{2,4} ',line):
        hashes,title=line.split(' ',1);doc.add_heading(title,level=len(hashes)-1)
    else:
        p=doc.add_paragraph();inline(p,line)
        if cover:p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(18)
        if line.startswith('Nota.'):
            p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(8)
            for run in p.runs:run.font.size=Pt(9.5)
        if re.match(r'^\[\d+\]',line):
            p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(8)
            for run in p.runs:run.font.size=Pt(10.5)
    i+=1
out=F/(NAME+'.docx');doc.save(out)
report={'word':out.name,'tablas':nt,'figuras':nf,'referencias_cruzadas_word':cross_fields,'marcadores':bookmark_id,'margenes_cm':2.54,'tipografia':'Times New Roman 12','interlineado':1.5,'tabla_min_pt':9,'pagina':'Carta','sin_saltos_entre_capitulos':True}
(O/'verificacion_word.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
