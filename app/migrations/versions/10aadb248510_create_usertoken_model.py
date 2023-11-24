"""Create UserToken model

Revision ID: 10aadb248510
Revises: ad2c6e3d5bc6
Create Date: 2023-11-24 02:27:14.562312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10aadb248510'
down_revision: Union[str, None] = 'ad2c6e3d5bc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_token',
    sa.Column('uuid', sa.String(), nullable=False),
    sa.Column('refresh_token', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('uuid', 'refresh_token')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_token')
    # ### end Alembic commands ###
