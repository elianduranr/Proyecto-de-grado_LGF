"""Prove unchanged historical rows before sharing an append-only SQL source version."""
import itertools
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


def blocks(path,date_column=None,cutoff=None,newer=False,size=10000):
    pending=None
    for batch in pq.ParquetFile(path).iter_batches(batch_size=size):
        table=pa.Table.from_batches([batch]).replace_schema_metadata(None)
        if date_column:
            dates=table[date_column]
            bound=pa.scalar(cutoff,type=dates.type)
            mask=pc.fill_null(pc.greater(dates,bound),False) if newer else pc.fill_null(pc.less_equal(dates,bound),True)
            table=table.filter(mask)
        if not len(table):continue
        pending=table if pending is None else pa.concat_tables([pending,table])
        while len(pending)>=size:
            yield pending.slice(0,size).combine_chunks().to_batches()[0]
            pending=pending.slice(size)
    if pending is not None and len(pending):yield pending.combine_chunks().to_batches()[0]


def unchanged_history(old_path,new_path,date_column,cutoff):
    old=blocks(old_path)
    current=blocks(new_path,date_column,cutoff)
    sentinel=object()
    for left,right in itertools.zip_longest(old,current,fillvalue=sentinel):
        if left is sentinel or right is sentinel or not left.equals(right):return False
    return True
