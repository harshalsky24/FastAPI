"""initial supers

Revision ID: ffa671b97d8e
Revises: 3b9801838d0a
Create Date: 2025-02-17 14:09:00.197866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffa671b97d8e'
down_revision: Union[str, None] = '3b9801838d0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('organizations_super_admin_id_fkey', 'organizations', type_='foreignkey')
    op.create_foreign_key(None, 'organizations', 'users', ['super_admin_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'organizations', type_='foreignkey')
    op.create_foreign_key('organizations_super_admin_id_fkey', 'organizations', 'users', ['super_admin_id'], ['id'])
    # ### end Alembic commands ###
