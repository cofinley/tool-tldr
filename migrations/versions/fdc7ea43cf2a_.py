"""Add deleted field

Revision ID: fdc7ea43cf2a
Revises: 9f9cae7ab545
Create Date: 2018-04-07 19:06:21.671360

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fdc7ea43cf2a'
down_revision = '9f9cae7ab545'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted', sa.DateTime(), nullable=True))
        batch_op.alter_column('is_time_travel_edit',
                              existing_type=mysql.TINYINT(display_width=1),
                              type_=sa.Boolean(),
                              existing_nullable=True)

    with op.batch_alter_table('categories_version', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted', sa.DateTime(), autoincrement=False, nullable=True))
        batch_op.alter_column('is_time_travel_edit',
                              existing_type=mysql.TINYINT(display_width=1),
                              type_=sa.Boolean(),
                              existing_nullable=True,
                              autoincrement=False)

    with op.batch_alter_table('tools', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted', sa.DateTime(), nullable=True))
        batch_op.alter_column('is_active',
                              existing_type=mysql.TINYINT(display_width=1),
                              type_=sa.Boolean(),
                              existing_nullable=True)
        batch_op.alter_column('is_time_travel_edit',
                              existing_type=mysql.TINYINT(display_width=1),
                              type_=sa.Boolean(),
                              existing_nullable=True)

    with op.batch_alter_table('tools_version', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted', sa.DateTime(), autoincrement=False, nullable=True))
        batch_op.alter_column('is_active',
                              existing_type=mysql.TINYINT(display_width=1),
                              type_=sa.Boolean(),
                              existing_nullable=True,
                              autoincrement=False)
        batch_op.alter_column('is_time_travel_edit',
                              existing_type=mysql.TINYINT(display_width=1),
                              type_=sa.Boolean(),
                              existing_nullable=True,
                              autoincrement=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted', sa.DateTime(), nullable=True))
        batch_op.alter_column('about_me',
                              existing_type=mysql.TEXT(),
                              type_=sa.Text(length=500),
                              existing_nullable=True)
        batch_op.alter_column('confirmed',
                              existing_type=mysql.TINYINT(display_width=1),
                              type_=sa.Boolean(),
                              existing_nullable=True)
        batch_op.alter_column('is_blocked',
                              existing_type=mysql.TINYINT(display_width=1),
                              type_=sa.Boolean(),
                              existing_nullable=True)

        # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('is_blocked',
                              existing_type=sa.Boolean(),
                              type_=mysql.TINYINT(display_width=1),
                              existing_nullable=True)
        batch_op.alter_column('confirmed',
                              existing_type=sa.Boolean(),
                              type_=mysql.TINYINT(display_width=1),
                              existing_nullable=True)
        batch_op.alter_column('about_me',
                              existing_type=sa.Text(length=500),
                              type_=mysql.TEXT(),
                              existing_nullable=True)
        batch_op.drop_column('deleted')

    with op.batch_alter_table('tools_version', schema=None) as batch_op:
        batch_op.alter_column('is_time_travel_edit',
                              existing_type=sa.Boolean(),
                              type_=mysql.TINYINT(display_width=1),
                              existing_nullable=True,
                              autoincrement=False)
        batch_op.alter_column('is_active',
                              existing_type=sa.Boolean(),
                              type_=mysql.TINYINT(display_width=1),
                              existing_nullable=True,
                              autoincrement=False)
        batch_op.drop_column('deleted')

    with op.batch_alter_table('tools', schema=None) as batch_op:
        batch_op.alter_column('is_time_travel_edit',
                              existing_type=sa.Boolean(),
                              type_=mysql.TINYINT(display_width=1),
                              existing_nullable=True)
        batch_op.alter_column('is_active',
                              existing_type=sa.Boolean(),
                              type_=mysql.TINYINT(display_width=1),
                              existing_nullable=True)
        batch_op.drop_column('deleted')

    with op.batch_alter_table('categories_version', schema=None) as batch_op:
        batch_op.alter_column('is_time_travel_edit',
                              existing_type=sa.Boolean(),
                              type_=mysql.TINYINT(display_width=1),
                              existing_nullable=True,
                              autoincrement=False)
        batch_op.drop_column('deleted')

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.alter_column('is_time_travel_edit',
                              existing_type=sa.Boolean(),
                              type_=mysql.TINYINT(display_width=1),
                              existing_nullable=True)
        batch_op.drop_column('deleted')

        # ### end Alembic commands ###
