"""Your migration message

Revision ID: b3309478fdca
Revises: 64409c1d2e88
Create Date: 2024-02-18 11:43:23.840492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3309478fdca'
down_revision: Union[str, None] = '64409c1d2e88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'files', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'files', type_='foreignkey')
    op.drop_column('files', 'user_id')
    # ### end Alembic commands ###
