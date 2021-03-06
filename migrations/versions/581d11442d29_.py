"""empty message

Revision ID: 581d11442d29
Revises: c6eb46eb0d5f
Create Date: 2021-03-05 02:43:35.727417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '581d11442d29'
down_revision = 'c6eb46eb0d5f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('entry', sa.Column('simulation_successfull', sa.Boolean(), nullable=True))
    op.drop_column('entry', 'simulation_succesfull')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('entry', sa.Column('simulation_succesfull', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('entry', 'simulation_successfull')
    # ### end Alembic commands ###