"""Add columns to competition

Revision ID: 7696ed1c2bd3
Revises: 4301546e6ec3
Create Date: 2018-03-04 19:00:08.102906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7696ed1c2bd3'
down_revision = '4301546e6ec3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('competitions', sa.Column('games_in_season', sa.Integer(), nullable=True))
    op.add_column('competitions', sa.Column('shortcode', sa.String(), nullable=True))
    op.add_column('competitions', sa.Column('teams_in_competition', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('competitions', 'teams_in_competition')
    op.drop_column('competitions', 'shortcode')
    op.drop_column('competitions', 'games_in_season')
    # ### end Alembic commands ###