"""Inspección acotada: no carga celdas, estilos, cadenas compartidas ni cachés."""
import posixpath
import re
from zipfile import ZipFile
from xml.etree import ElementTree as ET


def small_xml(book, name):
    if book.getinfo(name).file_size > 4*1024*1024:
        raise ValueError('El índice del libro Excel es demasiado grande para una carga válida.')
    return ET.fromstring(book.read(name))


def dimensions(book, name):
    parser=ET.XMLPullParser(events=['start'])
    # Excel normalmente declara dimension antes de sheetData. Sin dimension no
    # recorremos millones de celdas sólo para presentar un número aproximado.
    with book.open(name) as stream:
        for _ in range(16):
            chunk=stream.read(4096)
            if not chunk:break
            parser.feed(chunk)
            for _,element in parser.read_events():
                tag=element.tag.rsplit('}',1)[-1]
                if tag=='dimension':
                    match=re.fullmatch(r'\$?([A-Z]+)\$?(\d+)',element.get('ref','').split(':')[-1])
                    if match:
                        columns=0
                        for char in match[1]:columns=columns*26+ord(char)-64
                        return int(match[2]),columns
                    return None,None
                if tag=='sheetData':return None,None
    return None,None


def inspect_workbook(path):
    with ZipFile(path) as book:
        if sum(item.file_size for item in book.infolist())>3*1024*1024*1024:
            raise ValueError('El libro descomprimido excede el límite de 3 GB.')
        if '[Content_Types].xml' not in book.namelist():
            raise ValueError('El archivo no es un libro Excel válido.')
        workbook=small_xml(book,'xl/workbook.xml')
        relationships={r.get('Id'):r for r in small_xml(book,'xl/_rels/workbook.xml.rels')}
        result=[]
        for element in workbook.iter():
            if element.tag.rsplit('}',1)[-1]!='sheet':continue
            rid=next((v for k,v in element.attrib.items() if k.endswith('}id')),None)
            relation=relationships.get(rid)
            if relation is None or relation.get('TargetMode')=='External':
                raise ValueError('El índice de hojas del libro es inválido.')
            target=relation.get('Target','')
            name=posixpath.normpath(target.lstrip('/') if target.startswith('/') else 'xl/'+target)
            if not name.startswith('xl/') or name not in book.namelist():
                raise ValueError('No se encontró una hoja declarada en el libro.')
            if not relation.get('Type','').endswith('/worksheet'):continue
            rows,columns=dimensions(book,name)
            result.append({'name':element.get('name'),'rows':rows,'columns':columns})
        if not result:raise ValueError('El libro no contiene hojas de datos.')
        return result
