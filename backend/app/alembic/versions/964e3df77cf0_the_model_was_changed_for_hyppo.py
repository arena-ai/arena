"""The model was changed for Hyppo

Revision ID: 964e3df77cf0
Revises: deac92ea807e
Create Date: 2024-10-02 16:30:15.774103

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '964e3df77cf0'
down_revision = 'deac92ea807e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documentdataexample', sa.Column('start_page', sa.Integer(), nullable=False))
    op.add_column('documentdataexample', sa.Column('end_page', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('documentdataexample', 'end_page')
    op.drop_column('documentdataexample', 'start_page')
    # ### end Alembic commands ###