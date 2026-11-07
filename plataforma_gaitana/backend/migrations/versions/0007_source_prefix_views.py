"""Keep historical source versions stable when new closed days are appended."""
from alembic import op

revision='0007'
down_revision='0006'
branch_labels=None
depends_on=None

VIEWS={'produccion_real':'produccion_real_limpio','clima':'clima_limpio',
       'planos_siembra':'planos_siembra_limpio','curvas_variedad':'curvas_variedad_limpio',
       'estimados_semanales':'estimados_semanales_limpio'}


def upgrade():
    if op.get_bind().dialect.name!='mssql':return
    for view,source in VIEWS.items():
        op.execute(f"ALTER VIEW [EP].[vw_lgf_{view}] AS SELECT s.* FROM [EP].[lgf_{source}] s JOIN [EP].[lgf_dataset_sources] b ON b.source_dataset_id=s.dataset_id AND b.source_name='{source}' JOIN [EP].[lgf_active_dataset] a ON a.dataset_id=b.dataset_id AND a.id='vigente' WHERE s.row_number<b.rows")


def downgrade():
    raise RuntimeError('No se elimina el límite de versiones históricas sin un plan explícito.')
