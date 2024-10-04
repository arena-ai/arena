"""rename pydantic_model as response_template

Revision ID: 574e7b2875b3
Revises: 4e92c62b7d90
Create Date: 2024-10-04 09:02:06.439343

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '574e7b2875b3'
down_revision = '4e92c62b7d90'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documentdataextractor', sa.Column('response_template', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.drop_column('documentdataextractor', 'pydantic_model')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documentdataextractor', sa.Column('pydantic_model', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('documentdataextractor', 'response_template')
    # ### end Alembic commands ###
