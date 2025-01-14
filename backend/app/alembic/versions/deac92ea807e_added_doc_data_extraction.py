"""Added doc data extraction

Revision ID: deac92ea807e
Revises: 23a9e2f29a02
Create Date: 2024-09-19 11:44:56.835034

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "deac92ea807e"
down_revision = "23a9e2f29a02"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "documentdataextractor",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "prompt", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_documentdataextractor_name"),
        "documentdataextractor",
        ["name"],
        unique=True,
    )
    op.create_table(
        "documentdataexample",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "document_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("data", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("document_data_extractor_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["document_data_extractor_id"],
            ["documentdataextractor.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("documentdataexample")
    op.drop_index(
        op.f("ix_documentdataextractor_name"),
        table_name="documentdataextractor",
    )
    op.drop_table("documentdataextractor")
    # ### end Alembic commands ###
