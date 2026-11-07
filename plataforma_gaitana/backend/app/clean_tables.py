"""Typed SQL schemas captured from the actual validated Parquet columns."""
import json
from pathlib import Path
import sqlalchemy as sa
from sqlalchemy.dialects.mssql import DATETIME2
from .db import Base

SCHEMAS = json.loads((Path(__file__).parents[1] / 'migrations/source_schema_0002.json').read_text(encoding='utf-8'))
TEXT_LENGTH=500
TYPES = {'text': lambda:sa.Unicode(TEXT_LENGTH), 'integer': sa.BigInteger, 'float': sa.Float,
         'boolean': sa.Boolean, 'datetime': lambda:sa.DateTime().with_variant(DATETIME2(), 'mssql')}
CLEAN_TABLES = {
    name: sa.Table('lgf_' + name, Base.metadata,
        sa.Column('dataset_id', sa.String(36), sa.ForeignKey('lgf_datasets.id'), primary_key=True),
        sa.Column('row_number', sa.BigInteger, primary_key=True),
        *(sa.Column(field['name'], TYPES[field['type']](), nullable=True) for field in fields))
    for name, fields in SCHEMAS.items()
}
