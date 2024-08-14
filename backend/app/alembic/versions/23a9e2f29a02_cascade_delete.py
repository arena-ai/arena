"""cascade delete

Revision ID: 23a9e2f29a02
Revises: a3b5b8f12daf
Create Date: 2024-07-23 10:09:57.795034

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '23a9e2f29a02'
down_revision = 'a3b5b8f12daf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('event', 'owner_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint('event_parent_id_fkey', 'event', type_='foreignkey')
    op.drop_constraint('event_owner_id_fkey', 'event', type_='foreignkey')
    op.create_foreign_key(None, 'event', 'user', ['owner_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'event', 'event', ['parent_id'], ['id'], ondelete='CASCADE')
    op.alter_column('eventattribute', 'event_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('eventattribute', 'attribute_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint('eventattribute_attribute_id_fkey', 'eventattribute', type_='foreignkey')
    op.drop_constraint('eventattribute_event_id_fkey', 'eventattribute', type_='foreignkey')
    op.create_foreign_key(None, 'eventattribute', 'event', ['event_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'eventattribute', 'attribute', ['attribute_id'], ['id'], ondelete='CASCADE')
    op.alter_column('eventidentifier', 'event_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint('eventidentifier_event_id_fkey', 'eventidentifier', type_='foreignkey')
    op.create_foreign_key(None, 'eventidentifier', 'event', ['event_id'], ['id'], ondelete='CASCADE')
    op.alter_column('setting', 'owner_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('setting', 'owner_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint(None, 'eventidentifier', type_='foreignkey')
    op.create_foreign_key('eventidentifier_event_id_fkey', 'eventidentifier', 'event', ['event_id'], ['id'])
    op.alter_column('eventidentifier', 'event_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint(None, 'eventattribute', type_='foreignkey')
    op.drop_constraint(None, 'eventattribute', type_='foreignkey')
    op.create_foreign_key('eventattribute_event_id_fkey', 'eventattribute', 'event', ['event_id'], ['id'])
    op.create_foreign_key('eventattribute_attribute_id_fkey', 'eventattribute', 'attribute', ['attribute_id'], ['id'])
    op.alter_column('eventattribute', 'attribute_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('eventattribute', 'event_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint(None, 'event', type_='foreignkey')
    op.drop_constraint(None, 'event', type_='foreignkey')
    op.create_foreign_key('event_owner_id_fkey', 'event', 'user', ['owner_id'], ['id'])
    op.create_foreign_key('event_parent_id_fkey', 'event', 'event', ['parent_id'], ['id'])
    op.alter_column('event', 'owner_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
