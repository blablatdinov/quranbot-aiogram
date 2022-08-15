"""Create prayer models.

Revision ID: 23858449989b
Revises: 72297b274c99
Create Date: 2022-08-15 11:23:53.564665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23858449989b'
down_revision = '72297b274c99'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prayer_days',
    sa.Column('date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('date')
    )
    op.create_table('prayers_at_user_groups',
    sa.Column('prayers_at_user_group_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('prayers_at_user_group_id')
    )
    op.create_table('prayers',
    sa.Column('prayer_id', sa.String(), nullable=False),
    sa.Column('time', sa.Time(), nullable=False),
    sa.Column('city_id', sa.String(), nullable=True),
    sa.Column('day_id', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['city_id'], ['cities.city_id'], ),
    sa.ForeignKeyConstraint(['day_id'], ['prayer_days.date'], ),
    sa.PrimaryKeyConstraint('prayer_id')
    )
    op.create_table('prayers_at_user',
    sa.Column('prayer_at_user_id', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('prayer_id', sa.String(), nullable=True),
    sa.Column('day_id', sa.Date(), nullable=True),
    sa.Column('prayer_group_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['day_id'], ['prayer_days.date'], ),
    sa.ForeignKeyConstraint(['prayer_group_id'], ['prayers_at_user_groups.prayers_at_user_group_id'], ),
    sa.ForeignKeyConstraint(['prayer_id'], ['prayers.prayer_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.chat_id'], ),
    sa.PrimaryKeyConstraint('prayer_at_user_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prayers_at_user')
    op.drop_table('prayers')
    op.drop_table('prayers_at_user_groups')
    op.drop_table('prayer_days')
    # ### end Alembic commands ###