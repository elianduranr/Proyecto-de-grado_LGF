from zipfile import ZipFile, ZIP_DEFLATED
import openpyxl
from app.xlsx_header import inspect_workbook


def test_inspection_reads_header_without_opening_shared_strings_or_cells(tmp_path,monkeypatch):
    path=tmp_path/'large.xlsx'
    workbook=openpyxl.Workbook();workbook.active.title='BD';workbook.active.append(['DATE','VALUE']);workbook.save(path)
    with ZipFile(path,'a',compression=ZIP_DEFLATED) as archive:
        archive.writestr('xl/sharedStrings.xml',b'<sst>'+b'not loaded'*1_000_000+b'</sst>')
    original=ZipFile.open
    def guarded(self,name,*args,**kwargs):
        assert str(name)!='xl/sharedStrings.xml'
        return original(self,name,*args,**kwargs)
    monkeypatch.setattr(ZipFile,'open',guarded)
    assert inspect_workbook(path)==[{'name':'BD','rows':1,'columns':2}]
