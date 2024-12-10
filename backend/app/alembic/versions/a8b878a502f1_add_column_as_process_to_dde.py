"""Add column as_process to dde

Revision ID: a8b878a502f1
Revises: 5b09eca9fc4d
Create Date: 2024-12-05 10:00:45.060030

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'a8b878a502f1'
down_revision = '5b09eca9fc4d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documentdataextractor', sa.Column('process_as', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('documentdataextractor', 'process_as')
    # ### end Alembic commands ###