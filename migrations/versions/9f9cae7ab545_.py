"""Add activity table

Revision ID: 9f9cae7ab545
Revises: 3cd66eac7cd6
Create Date: 2018-03-12 21:20:32.582986

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = '9f9cae7ab545'
down_revision = '3cd66eac7cd6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('activity',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('verb', sa.Unicode(length=255), nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), nullable=False),
    sa.Column('data', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('object_type', sa.String(length=255), nullable=True),
    sa.Column('object_id', sa.BigInteger(), nullable=True),
    sa.Column('object_tx_id', sa.BigInteger(), nullable=True),
    sa.Column('target_type', sa.String(length=255), nullable=True),
    sa.Column('target_id', sa.BigInteger(), nullable=True),
    sa.Column('target_tx_id', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_activity_transaction_id'), ['transaction_id'], unique=False)

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.alter_column('is_time_travel_edit',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)

    with op.batch_alter_table('categories_version', schema=None) as batch_op:
        batch_op.alter_column('is_time_travel_edit',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True,
               autoincrement=False)

    with op.batch_alter_table('tools', schema=None) as batch_op:
        batch_op.alter_column('is_active',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
        batch_op.alter_column('is_time_travel_edit',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)

    with op.batch_alter_table('tools_version', schema=None) as batch_op:
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

    with op.batch_alter_table('tools', schema=None) as batch_op:
        batch_op.alter_column('is_time_travel_edit',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
        batch_op.alter_column('is_active',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)

    with op.batch_alter_table('categories_version', schema=None) as batch_op:
        batch_op.alter_column('is_time_travel_edit',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True,
               autoincrement=False)

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.alter_column('is_time_travel_edit',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)

    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_activity_transaction_id'))

    op.drop_table('activity')
    # ### end Alembic commands ###