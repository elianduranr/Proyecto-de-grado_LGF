"""Track active source files without duplicating raw Excel contents in SQL."""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    schema = 'EP' if op.get_bind().dialect.name == 'mssql' else None
    ref = f'{schema}.lgf_datasets.id' if schema else 'lgf_datasets.id'
    op.create_table('lgf_source_files',
        sa.Column('path', sa.String(400), primary_key=True),
        sa.Column('source', sa.String(40), nullable=False),
        sa.Column('sha256', sa.String(64), nullable=False),
        sa.Column('original_sha256', sa.String(64), nullable=True),
        sa.Column('active', sa.Integer(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('dataset_id', sa.String(36), sa.ForeignKey(ref), nullable=False), schema=schema)


def downgrade():
    raise RuntimeError('La reversión destructiva requiere respaldo y un plan explícito.')
