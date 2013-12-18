"""empty message

Revision ID: 4fa66a99c1dd
Revises: 39939c989fb1
Create Date: 2013-11-08 00:02:57.894562

"""

# revision identifiers, used by Alembic.
revision = '4fa66a99c1dd'
down_revision = '39939c989fb1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_listed', sa.Boolean(), nullable=True, server_default="True"))
    op.alter_column('user', 'is_listed', server_default=None)
    op.drop_column('user', u'premium_until')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column(u'premium_until', postgresql.TIMESTAMP(), nullable=True))
    op.drop_column('user', 'is_listed')
    ### end Alembic commands ###
