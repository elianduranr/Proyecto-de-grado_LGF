"""Reuse unchanged normalized source batches across dataset versions."""
from alembic import op
import sqlalchemy as sa

revision='0004'
down_revision='0003'
branch_labels=None
depends_on=None


def upgrade():
    schema='EP' if op.get_bind().dialect.name=='mssql' else None
    ref=f'{schema}.lgf_datasets.id' if schema else 'lgf_datasets.id'
    op.create_table('lgf_dataset_sources',
        sa.Column('dataset_id',sa.String(36),sa.ForeignKey(ref),primary_key=True),
        sa.Column('source_name',sa.String(60),primary_key=True),
        sa.Column('source_dataset_id',sa.String(36),sa.ForeignKey(ref),nullable=False),
        sa.Column('rows',sa.BigInteger(),nullable=False),
        sa.Column('sha256',sa.String(64),nullable=False),schema=schema)
    prefix='[EP].' if schema else ''
    for source in ['produccion_real','clima','planos_siembra','curvas_variedad','estimados_semanales']:
        op.execute(sa.text(f"""CREATE VIEW {prefix}[vw_lgf_{source}] AS
            SELECT clean.* FROM {prefix}[lgf_{source}_limpio] AS clean
            INNER JOIN {prefix}[lgf_dataset_sources] AS version
              ON version.source_dataset_id=clean.dataset_id
              AND version.source_name='{source}_limpio'
            INNER JOIN {prefix}[lgf_active_dataset] AS active
              ON active.dataset_id=version.dataset_id AND active.id='vigente'"""))


def downgrade():
    raise RuntimeError('La reversión destructiva requiere respaldo y un plan explícito.')
