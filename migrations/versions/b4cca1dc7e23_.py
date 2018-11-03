"""Add 'what' section to tools

Revision ID: b4cca1dc7e23
Revises: dced42ca3e74
Create Date: 2018-05-27 18:17:49.741327

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b4cca1dc7e23'
down_revision = 'dced42ca3e74'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('tools', schema=None) as batch_op:
        batch_op.add_column(sa.Column('what', sa.String(length=250), nullable=True))

    with op.batch_alter_table('tools_version', schema=None) as batch_op:
        batch_op.add_column(sa.Column('what', sa.String(length=250), autoincrement=False, nullable=True))

        # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('tools_version', schema=None) as batch_op:
        batch_op.drop_column('what')

    with op.batch_alter_table('tools', schema=None) as batch_op:
        batch_op.drop_column('what')

        # ### end Alembic commands ###