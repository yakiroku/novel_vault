"""add_novels_completed

Revision ID: 2be3b30fcb0d
Revises: 5e87064bebe4
Create Date: 2025-01-14 11:18:10.545967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2be3b30fcb0d'
down_revision: Union[str, None] = '5e87064bebe4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('novels', sa.Column('completed', sa.Boolean(), nullable=False))
    op.create_index(op.f('ix_novels_completed'), 'novels', ['completed'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_novels_completed'), table_name='novels')
    op.drop_column('novels', 'completed')
    # ### end Alembic commands ###