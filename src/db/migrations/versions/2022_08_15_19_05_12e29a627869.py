"""Add File.link.

Revision ID: 12e29a627869
Revises: d6aa2e3f6fb1
Create Date: 2022-08-15 19:05:28.738951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12e29a627869'
down_revision = 'd6aa2e3f6fb1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('link', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('files', 'link')
    # ### end Alembic commands ###
