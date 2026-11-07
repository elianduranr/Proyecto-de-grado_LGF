"""Avoid ODBC LOB streaming for short source strings; never truncate values."""
import json
from pathlib import Path
import sqlalchemy as sa
from alembic import op

revision='0005'
down_revision='0004'
branch_labels=None
depends_on=None


def upgrade():
    if op.get_bind().dialect.name!='mssql':return
    definitions=json.loads((Path(__file__).parents[1]/'source_schema_0002.json').read_text(encoding='utf-8'))
    for name,fields in definitions.items():
        text_columns=[field['name'] for field in fields if field['type']=='text']
        if not op.get_context().as_sql:
            expressions=','.join(f'MAX(DATALENGTH([{column}]))' for column in text_columns)
            lengths=op.get_bind().execute(sa.text(f'SELECT {expressions} FROM [EP].[lgf_{name}]')).one()
            if any(length is not None and length>1000 for length in lengths):
                raise RuntimeError(f'Hay textos de más de 500 unidades UTF-16 en {name}; se conservan los valores y debe ampliarse el contrato.')
        for column in text_columns:
            op.alter_column('lgf_'+name,column,existing_type=sa.UnicodeText(),type_=sa.Unicode(500),existing_nullable=True,schema='EP')


def downgrade():
    raise RuntimeError('Los cambios de estructura requieren un plan explícito.')
