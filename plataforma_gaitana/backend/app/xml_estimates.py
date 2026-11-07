"""Bounded XML batches: retain the notebook's decoding and exact ESTIMADO filter."""
import re
import hashlib
from functools import wraps
from pathlib import Path
import joblib
from lxml import etree


def cache_reader(folder,notebook_hash):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    implementation=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    def decorate(reader):
        @wraps(reader)
        def wrapped(path):
            digest=hashlib.sha256((notebook_hash+implementation).encode('ascii'))
            with Path(path).open('rb') as stream:
                for block in iter(lambda:stream.read(4*1024*1024),b''):digest.update(block)
            cache=folder/(digest.hexdigest()+'.joblib')
            if cache.exists():
                # This directory contains only caches written by the worker, never uploads.
                return joblib.load(cache)
            result=reader(path)
            temp=cache.with_suffix('.part');joblib.dump(result,temp);temp.replace(cache)
            return result
        return wrapped
    return decorate


def estimated_rows(book, records, namespace, columns, shared, type_position, decode, normalize):
    allowed=[str(i) for i,value in enumerate(shared[type_position]) if normalize(value)=='ESTIMADO']
    position=type_position+1
    shared_filter=' or '.join(f'number(@v)={index}' for index in allowed) or 'false()'
    # Shared values are normalized once. Direct values still pass through the original decoder/filter.
    condition=f'*[{position}][not(self::m:x) or ({shared_filter})]'
    select=etree.XPath(f'./m:r[{condition}]',namespaces={'m':namespace})
    field=rb'\s*<[A-Za-z_][\w.-]*\b[^<>]*/>'
    row_start=rb'<r(?:\s[^<>]*)?>'
    row_shape=re.compile(row_start+rb'(?:'+field+rb')*\s*</r>|<r\s*/>')
    numbers=b'|'.join(index.encode('ascii') for index in allowed) or b'(?!)'
    shared_type=rb'\s*<x\b(?=[^<>]*\bv=[\"\x27]0*(?:'+numbers+rb')[\"\x27])[^<>]*/>'
    direct_type=rb'\s*<(?!x\b)[A-Za-z_][\w.-]*\b[^<>]*/>'
    matching_row=re.compile(row_start+rb'(?:'+field+rb'){'+str(type_position).encode('ascii')+rb'}(?:'+shared_type+rb'|'+direct_type+rb')(?:'+field+rb')*\s*</r>')
    closing=b'</pivotCacheRecords>'
    with book.open(records) as stream:
        data=stream.read(1024*1024)
        opening=re.search(rb'<pivotCacheRecords\b[^>]*>',data)
        if opening is None:
            # Preserve compatibility with an unusual namespace prefix using the original streaming path.
            with book.open(records) as fallback:
                for _,row in etree.iterparse(fallback,events=('end',),tag=f'{{{namespace}}}r'):
                    cells=list(row)
                    kind=decode(cells[type_position],shared[type_position]) if len(cells)>type_position else None
                    if normalize(kind)=='ESTIMADO':
                        yield [decode(cells[i],shared[i]) if i<len(cells) else None for i in range(len(columns))]
                    row.clear()
                    while row.getprevious() is not None:del row.getparent()[0]
            return
        prefix=opening.group()
        buffer=data[opening.end():]
        while True:
            last=buffer.rfind(b'</r>')
            if last>=0:
                complete,buffer=buffer[:last+4],buffer[last+4:]
                # Standard Excel cache rows contain only self-closing scalar cells. Verify
                # that shape for the entire batch before filtering bytes; unusual XML uses
                # the general parser. Decoding and final filtering remain the original code.
                if not row_shape.sub(b'',complete).strip():
                    complete=b''.join(match.group() for match in matching_row.finditer(complete))
                root=etree.fromstring(prefix+complete+closing)
                for row in select(root):
                    cells=list(row)
                    kind=decode(cells[type_position],shared[type_position]) if len(cells)>type_position else None
                    if normalize(kind)=='ESTIMADO':
                        yield [decode(cells[i],shared[i]) if i<len(cells) else None for i in range(len(columns))]
            block=stream.read(1024*1024)
            if not block:break
            buffer+=block
        # Validate any remaining XML instead of silently accepting a truncated document.
        tail=buffer.rsplit(closing,1)
        if len(tail)!=2:raise ValueError('XML de estimados incompleto.')
        etree.fromstring(prefix+tail[0]+closing)
