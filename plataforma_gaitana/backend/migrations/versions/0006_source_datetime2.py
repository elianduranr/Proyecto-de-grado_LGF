"""Preserve source dates and quality flags without SQL datetime range loss."""
import json
from pathlib import Path
import sqlalchemy as sa
from sqlalchemy.dialects.mssql import DATETIME2
from alembic import op

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name != 'mssql':
        return
    definitions = json.loads((Path(__file__).parents[1] / 'source_schema_0002.json').read_text(encoding='utf-8'))
    for name, fields in definitions.items():
        for field in fields:
            if field['type'] == 'datetime':
                op.alter_column('lgf_' + name, field['name'], existing_type=sa.DateTime(),
                                type_=DATETIME2(), existing_nullable=True, schema='EP')


def downgrade():
    raise RuntimeError('No se reduce el rango de fechas sin validar y respaldar los datos.')
