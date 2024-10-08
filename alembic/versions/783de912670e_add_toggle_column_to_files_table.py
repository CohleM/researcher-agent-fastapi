"""Add toggle column to files table

Revision ID: 783de912670e
Revises: 80d31fcd516b
Create Date: 2024-01-30 09:25:20.180797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '783de912670e'
down_revision: Union[str, None] = '80d31fcd516b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('toggle', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('files', 'toggle')
    # ### end Alembic commands ###
