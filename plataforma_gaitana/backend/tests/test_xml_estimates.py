import unicodedata
from zipfile import ZipFile
import pandas as pd
from lxml import etree
from app.xml_estimates import estimated_rows,cache_reader


def normalize(value):
    if value is None:return ''
    return ''.join(c for c in unicodedata.normalize('NFKD',str(value)) if not unicodedata.combining(c)).strip().upper()


def decode(cell,shared):
    kind=etree.QName(cell).localname
    if kind=='m':return None
    if kind=='x':return shared[int(cell.get('v'))]
    if kind=='n':return float(cell.get('v'))
    return cell.get('v')


def test_xml_filter_keeps_exact_values_order_and_direct_types(tmp_path):
    namespace='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    path=tmp_path/'book.xlsx'
    xml=f'''<pivotCacheRecords xmlns="{namespace}">
    <r><x v="1"/><n v="99"/></r>
    <r><x v="00"/><n v="17"/></r>
    <r><s v="  Éstimado  "/><n v="23"/></r>
    <r><m/><n v="200"/></r><r/>
    </pivotCacheRecords>'''
    with ZipFile(path,'w') as book:book.writestr('records.xml',xml)
    with ZipFile(path) as book:
        result=list(estimated_rows(book,'records.xml',namespace,['TIPO','TALLOS'],[['ESTIMADO','REAL'],[]],0,decode,normalize))
    assert result==[['ESTIMADO',17.0],['  Éstimado  ',23.0]]


def test_own_reader_cache_preserves_dtypes_attrs_and_invalidates_changed_file(tmp_path):
    source=tmp_path/'source.xlsx';source.write_bytes(b'first')
    calls=[]
    @cache_reader(tmp_path/'private_cache','notebook-version')
    def read(path):
        calls.append(path.read_bytes())
        frame=pd.DataFrame({'quantity':[1.0,None],'identity':['A',None]})
        frame.attrs={'cache_origen':'records1','refresco_cache_excel':46000.5}
        return frame
    original=read(source);restored=read(source)
    pd.testing.assert_frame_equal(original,restored);assert original.attrs==restored.attrs
    assert len(calls)==1
    source.write_bytes(b'second');read(source)
    assert len(calls)==2
