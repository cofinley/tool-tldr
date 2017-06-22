"""empty message

Revision ID: 30893572fa00
Revises: 0506d36f591a
Create Date: 2017-06-21 19:37:50.486429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30893572fa00'
down_revision = '0506d36f591a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tools_history',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=50), autoincrement=False, nullable=True),
    sa.Column('name_lower', sa.String(length=50), autoincrement=False, nullable=True),
    sa.Column('avatar_url', sa.String(length=150), autoincrement=False, nullable=True),
    sa.Column('parent_category_id', sa.Integer(), autoincrement=False, nullable=True),
    sa.Column('env', sa.String(length=30), autoincrement=False, nullable=True),
    sa.Column('created', sa.String(length=25), autoincrement=False, nullable=True),
    sa.Column('project_version', sa.String(length=10), autoincrement=False, nullable=True),
    sa.Column('link', sa.String(length=150), autoincrement=False, nullable=True),
    sa.Column('what', sa.String(length=200), autoincrement=False, nullable=True),
    sa.Column('why', sa.String(length=200), autoincrement=False, nullable=True),
    sa.Column('where', sa.String(length=200), autoincrement=False, nullable=True),
    sa.Column('version', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('changed', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', 'version')
    )
    with op.batch_alter_table('tools', schema=None) as batch_op:
        batch_op.add_column(sa.Column('project_version', sa.String(length=10), nullable=True))
        batch_op.alter_column('version',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tools', schema=None) as batch_op:
        batch_op.alter_column('version',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
        batch_op.drop_column('project_version')

    op.drop_table('tools_history')
    # ### end Alembic commands ###
