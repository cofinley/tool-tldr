"""Date created -> integer

Revision ID: 009c842174fe
Revises: 74c27597b164
Create Date: 2017-09-14 17:48:23.105977

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009c842174fe'
down_revision = '74c27597b164'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tools', 'created',
               existing_type=sa.DATETIME(),
               type_=sa.Integer(),
               existing_nullable=True)
    op.alter_column('tools_version', 'created',
               existing_type=sa.DATETIME(),
               type_=sa.Integer(),
               existing_nullable=True,
               autoincrement=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tools_version', 'created',
               existing_type=sa.Integer(),
               type_=sa.DATETIME(),
               existing_nullable=True,
               autoincrement=False)
    op.alter_column('tools', 'created',
               existing_type=sa.Integer(),
               type_=sa.DATETIME(),
               existing_nullable=True)
    # ### end Alembic commands ###
