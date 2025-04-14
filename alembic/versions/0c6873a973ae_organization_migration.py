"""organization migration

Revision ID: 0c6873a973ae
Revises: f0b4e3bc2590
Create Date: 2025-02-17 13:09:17.865133

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0c6873a973ae'
down_revision: Union[str, None] = 'f0b4e3bc2590'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Add a temporary NULL column first
def upgrade():
    op.add_column('organizations', sa.Column('super_admin_id', sa.Integer(), nullable=True))

    # Set a default super_admin_id for existing organizations (assuming user ID 1 is Super Admin)
    op.execute("UPDATE organizations SET super_admin_id = 1 WHERE super_admin_id IS NULL")

    # Now enforce NOT NULL constraint
    op.alter_column('organizations', 'super_admin_id', nullable=False)

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_organizations_super_admin_id', 
        'organizations', 
        'users', 
        ['super_admin_id'], 
        ['id'], 
        ondelete='CASCADE'
    )

# Rollback if needed
def downgrade():
    op.drop_constraint('fk_organizations_super_admin_id', 'organizations', type_='foreignkey')
    op.drop_column('organizations', 'super_admin_id')
