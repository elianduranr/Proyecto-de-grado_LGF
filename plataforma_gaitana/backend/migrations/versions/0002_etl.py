"""Dataset activation and normalized source tables in EP."""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    schema = 'EP' if op.get_bind().dialect.name == 'mssql' else None
    op.create_table('lgf_datasets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('state', sa.String(30), nullable=False),
        sa.Column('root', sa.Text(), nullable=False),
        sa.Column('manifest', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('activated_at', sa.DateTime(), nullable=True), schema=schema)
    ref = f'{schema}.lgf_datasets.id' if schema else 'lgf_datasets.id'
    op.create_table('lgf_active_dataset',
        sa.Column('id', sa.String(30), primary_key=True),
        sa.Column('dataset_id', sa.String(36), sa.ForeignKey(ref), nullable=False), schema=schema)
    # Frozen source schemas accompany this migration; no columns are inferred from an upload.
    import json
    from pathlib import Path
    definitions = json.loads((Path(__file__).parents[1] / 'source_schema_0002.json').read_text(encoding='utf-8'))
    types = {'text': sa.UnicodeText, 'integer': sa.BigInteger, 'float': sa.Float,
             'boolean': sa.Boolean, 'datetime': sa.DateTime}
    for name, fields in definitions.items():
        op.create_table('lgf_' + name,
            sa.Column('dataset_id', sa.String(36), sa.ForeignKey(ref), primary_key=True),
            sa.Column('row_number', sa.BigInteger, primary_key=True),
            *(sa.Column(f['name'], types[f['type']](), nullable=True) for f in fields), schema=schema)


def downgrade():
    raise RuntimeError('La reversión destructiva requiere respaldo y un plan explícito.')
